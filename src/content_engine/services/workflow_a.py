from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_a import (
    FilmingCard,
    HookType,
    VideoIntakeRecord,
    VideoHook,
    VideoPublishItem,
    VideoPublishStatus,
    VideoScript,
    VideoPlatform,
)


_VIDEO_PLATFORMS: set[str] = {"instagram", "tiktok", "youtube", "linkedin"}

HOOK_BLUEPRINTS: list[tuple[HookType, str]] = [
    ("market_warning", "Source-specific market warning from the collected source."),
    ("story_moment", "A buyer thinks price is the risk. It usually is not."),
    ("tactical_tip", "Check these three things before you trust a villa price tag."),
    ("data_stat_callout", "The listing price is rarely the full Bali cost."),
    ("bts_fragment", "What we notice on site before clients ever see the brochure."),
]


def build_video_intake_record(item: SourceItem) -> VideoIntakeRecord:
    raw_payload = item.raw_payload
    title = _first_text(
        raw_payload.get("video_title"),
        raw_payload.get("title"),
        _nested_text(raw_payload, "meta", "og:title"),
        item.source_name,
        item.content_theme.replace("_", " ").title(),
    )
    caption_text = _first_text(
        raw_payload.get("caption_text"),
        raw_payload.get("caption"),
        raw_payload.get("description"),
        _nested_text(raw_payload, "meta", "og:description"),
    )
    spoken_transcript = _first_text(
        raw_payload.get("spoken_transcript"),
        raw_payload.get("transcript"),
        raw_payload.get("video_transcript"),
        caption_text,
        item.transcript_text,
    )
    transcript_source = _first_text(
        raw_payload.get("transcript_source"),
        "source_text",
    )

    return VideoIntakeRecord(
        source_item_id=item.item_id,
        platform=_infer_video_platform(item),
        source_url=item.source_url,
        title=title,
        caption_text=caption_text,
        spoken_transcript=spoken_transcript,
        transcript_source=transcript_source,
        video_refs=_dedupe([item.source_url, *item.media_urls]),
        metrics=dict(item.engagement_signals),
        audience_segment=item.audience_segment,
        content_theme=item.content_theme,
        published_at=item.published_at,
    )


def develop_video_hooks(
    item: SourceItem,
    platform: VideoPlatform,
) -> list[VideoHook]:
    hooks: list[VideoHook] = []
    for index, (hook_type, default_line) in enumerate(HOOK_BLUEPRINTS, start=1):
        score = _score_hook(item, hook_type)
        hooks.append(
            VideoHook(
                hook_id=f"{item.item_id}_hook_{index}",
                source_item_id=item.item_id,
                platform=platform,
                content_theme=item.content_theme,
                angle=_hook_angle(item, hook_type),
                hook_text=_build_hook_text(item, hook_type, default_line),
                hook_type=hook_type,
                score=score,
            )
        )
    return hooks


def select_best_hook(hooks: list[VideoHook]) -> VideoHook:
    return sorted(hooks, key=lambda hook: hook.score, reverse=True)[0]


def build_video_script(
    hook: VideoHook,
    title: str,
    body_points: list[str],
    cta: str,
) -> VideoScript:
    script_text = "\n".join(
        [hook.hook_text, *body_points, cta]
    )
    return VideoScript(
        script_id=f"scr_{hook.hook_id}",
        source_item_id=hook.source_item_id,
        title=title,
        platform=hook.platform,
        hook_text=hook.hook_text,
        script_text=script_text,
        cta=cta,
        filming_priority=1,
        status="scripted",
    )


def build_filming_card(
    script: VideoScript,
    filming_priority: int,
) -> FilmingCard:
    return FilmingCard(
        card_id=f"film_{script.script_id}",
        linked_script_id=script.script_id,
        filming_priority=filming_priority,
        filmed=False,
    )


def build_video_publish_item(
    script: VideoScript,
    caption: str,
    publish_date: str | None = None,
) -> VideoPublishItem:
    status: VideoPublishStatus = "published" if publish_date else "ready"
    return VideoPublishItem(
        publish_item_id=f"pub_{script.script_id}",
        linked_script_id=script.script_id,
        platform=script.platform,
        caption=caption,
        publish_date=publish_date,
        status=status,
    )


def _score_hook(item: SourceItem, hook_type: str) -> int:
    score = 5
    if hook_type == "market_warning":
        score += 3
    if hook_type == "market_warning" and _source_verbatim_hook(item):
        score = 10
    if hook_type == "bts_fragment" and item.media_urls:
        score += 2
    if hook_type == "data_stat_callout" and any(value >= 1000 for value in item.engagement_signals.values()):
        score += 1
    return min(score, 10)


def _build_hook_text(item: SourceItem, hook_type: str, default_line: str) -> str:
    if hook_type == "market_warning":
        source_hook = _source_verbatim_hook(item)
        if source_hook:
            return source_hook

    theme = _video_hook_theme_key(item)
    subject = _video_hook_subject(item)
    if hook_type == "market_warning":
        return _video_market_warning_hook(theme, subject)
    if hook_type == "story_moment":
        return _video_story_moment_hook(theme, subject)
    if hook_type == "bts_fragment":
        return f"Behind the scenes: {item.transcript_text.split('.')[0].strip()}."
    if hook_type == "tactical_tip":
        return _video_tactical_tip_hook(theme, subject)
    if hook_type == "data_stat_callout":
        return _video_data_hook(theme, subject)
    return default_line


def _hook_angle(item: SourceItem, hook_type: str) -> str:
    if hook_type == "market_warning" and _source_verbatim_hook(item):
        return f"source verbatim hook for {item.audience_segment}"
    return f"{hook_type.replace('_', ' ')} for {item.audience_segment}"


def _source_verbatim_hook(item: SourceItem) -> str:
    raw_payload = item.raw_payload
    values = [
        raw_payload.get("source_hook"),
        raw_payload.get("detected_hook"),
        raw_payload.get("opening_line"),
        raw_payload.get("first_3_seconds"),
        raw_payload.get("hook"),
    ]
    hooks = raw_payload.get("hooks")
    if isinstance(hooks, list):
        values.extend(hooks)

    for value in values:
        if isinstance(value, str) and _looks_like_hook(value):
            return _normalize_space(value)
    return ""


def _looks_like_hook(value: str) -> bool:
    normalized = _normalize_space(value)
    word_count = len(normalized.split())
    return 4 <= word_count <= 28


def _video_market_warning_hook(theme: str, subject: str) -> str:
    hooks = {
        "legal_structure": f"In Bali, the real risk is not the price. It is the {subject} under it.",
        "land_structure": f"Bali land looks simple until the {subject} starts asking expensive questions.",
        "wellness_design": f"Wellness is not a moodboard anymore. It is a signal of {subject}.",
        "boutique_hospitality": f"A boutique hotel does not win on beauty. It wins on the {subject}.",
        "bali_travel": f"Bali is easy to film beautifully and hard to understand through {subject}.",
        "founder_life": f"The expensive mistake is building a life that only looks right from the outside.",
        "market_structure": f"In Bali, the headline price is not the signal. The {subject} is.",
    }
    return hooks.get(theme, f"The real story is not the surface. It is the {subject}.")


def _video_story_moment_hook(theme: str, subject: str) -> str:
    hooks = {
        "legal_structure": f"Someone sees a beautiful villa. We look for the {subject}.",
        "land_structure": f"The land looks calm until the {subject} enters the conversation.",
        "wellness_design": f"The room feels expensive because the {subject} was designed first.",
        "boutique_hospitality": f"The guest remembers the {subject}, not the expensive furniture.",
        "bali_travel": f"The postcard moment is easy. The {subject} is harder to fake.",
        "founder_life": f"A founder can protect ambition and family, but not by performing perfection.",
        "market_structure": f"A buyer sees the listing. An operator checks the {subject}.",
    }
    return hooks.get(theme, f"Everyone sees the content. We look for the {subject}.")


def _video_tactical_tip_hook(theme: str, subject: str) -> str:
    hooks = {
        "legal_structure": f"Before you trust the villa, check the {subject} first.",
        "land_structure": f"Before you trust the land story, check the {subject}.",
        "wellness_design": f"Before you add a spa, ask what {subject} the project actually creates.",
        "boutique_hospitality": f"Before you design the lobby, define the {subject}.",
        "bali_travel": f"Before you save the Bali spot, ask what {subject} it actually gives.",
        "founder_life": f"Before you copy a founder's lifestyle, ask what family and ambition are costing.",
        "market_structure": f"Before you trust the price, check the {subject}.",
    }
    return hooks.get(theme, f"Before you trust the idea, check the {subject}.")


def _video_data_hook(theme: str, subject: str) -> str:
    hooks = {
        "legal_structure": f"One missing {subject} can change the whole deal.",
        "land_structure": f"The {subject} can change the value faster than the view.",
        "wellness_design": f"The {subject} is becoming a business signal, not decoration.",
        "boutique_hospitality": f"The {subject} is where boutique hotels separate from pretty rooms.",
        "bali_travel": f"The {subject} is what separates useful Bali content from a postcard.",
        "founder_life": f"The metric nobody sees is the emotional cost of performing a perfect life.",
        "market_structure": f"The {subject} matters more than the first number on the listing.",
    }
    return hooks.get(theme, f"The {subject} is the signal most people skip.")


def _video_hook_theme_key(item: SourceItem) -> str:
    context = _source_context(item)
    if _contains_any(context, ("legal", "law", "lawyer", "zoning", "permit", "regulat", "юрид", "закон", "разреш")):
        return "legal_structure"
    if _contains_any(context, ("land", "зем", "leasehold", "freehold")):
        return "land_structure"
    if _contains_any(context, ("wellness", "spa", "biophilic", "restorative", "wellbeing")):
        return "wellness_design"
    if _contains_any(context, ("boutique", "hotel", "hospitality", "resort", "bensley", "guest")):
        return "boutique_hospitality"
    if _contains_any(context, ("travel", "itinerary", "beach", "restaurant", "balibible", "trip", "путеше")):
        return "bali_travel"
    if _contains_any(context, ("family", "child", "mother", "founder", "ambition", "entrepreneur", "сем", "реб", "мама", "амбици")):
        return "founder_life"
    if _contains_any(context, ("trend", "report", "market", "yield", "price", "villa", "operator", "resale", "property", "investor", "рын", "цен", "вилл")):
        return "market_structure"
    return "source_specific"


def _video_hook_subject(item: SourceItem) -> str:
    context = _source_context(item)
    subjects = [
        (("zoning", "permit", "разреш"), "zoning and permit layer"),
        (("legal", "law", "lawyer", "юрид", "закон"), "legal structure"),
        (("operator", "management", "operations", "оператор"), "operator reality"),
        (("resale", "liquidity", "exit", "ликвид"), "liquidity and exit path"),
        (("yield", "roi", "return", "доход"), "yield logic"),
        (("land", "зем", "leasehold", "freehold"), "land structure"),
        (("family", "child", "mother", "сем", "реб", "мама"), "family rituals"),
        (("ambition", "founder", "entrepreneur", "амбици"), "ambition without a perfect image"),
        (("wellness", "spa", "biophilic"), "restorative feeling"),
        (("boutique", "hotel", "hospitality", "resort"), "reason to return"),
        (("travel", "itinerary", "trip", "beach", "путеше"), "honest experience of place"),
        (("trend", "report", "market", "рын"), "market signal"),
    ]
    for markers, subject in subjects:
        if _contains_any(context, markers):
            return subject
    return _fallback_subject(item)


def _source_context(item: SourceItem) -> str:
    raw_values = " ".join(str(value) for value in item.raw_payload.values() if isinstance(value, (str, int, float)))
    return _normalize_space(
        " ".join(
            [
                item.source_name,
                item.source_type,
                item.content_theme,
                item.audience_segment,
                item.transcript_text,
                raw_values,
            ]
        )
    ).lower()


def _fallback_subject(item: SourceItem) -> str:
    theme = item.content_theme.replace("_", " ").strip()
    if theme:
        return f"{theme} signal"
    first_sentence = item.transcript_text.split(".")[0].strip()
    if first_sentence:
        return first_sentence[:80]
    return "source signal"


def _normalize_space(text: str) -> str:
    return " ".join(text.split()).strip()


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _infer_video_platform(item: SourceItem) -> VideoPlatform:
    platform = item.source_type.split("_", 1)[0]
    if platform in _VIDEO_PLATFORMS:
        return platform  # type: ignore[return-value]
    return "instagram"


def _first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return " ".join(value.split()).strip()
    return ""


def _nested_text(payload: dict, outer_key: str, inner_key: str) -> str:
    outer = payload.get(outer_key)
    if not isinstance(outer, dict):
        return ""
    value = outer.get(inner_key)
    if not isinstance(value, str):
        return ""
    return value


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
