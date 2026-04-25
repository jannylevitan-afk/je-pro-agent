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
    ("market_warning", "What looks cheap first is often the most expensive later."),
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
                angle=f"{hook_type.replace('_', ' ')} for {item.audience_segment}",
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
    if hook_type == "bts_fragment" and item.media_urls:
        score += 2
    if hook_type == "data_stat_callout" and any(value >= 1000 for value in item.engagement_signals.values()):
        score += 1
    return min(score, 10)


def _build_hook_text(item: SourceItem, hook_type: str, default_line: str) -> str:
    if hook_type == "bts_fragment":
        return f"Behind the scenes: {item.transcript_text.split('.')[0].strip()}."
    if hook_type == "tactical_tip":
        return "Before you trust the listing price, check legal risk, design quality, and management reality."
    return default_line


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
