from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import ContentBrief, InsightCard, SourceNote


SOURCE_THEME_HINTS = {
    "wellness_architecture": {
        "content_pillar": "expertise_lifestyle",
        "priority": 2,
    },
    "boutique_hotels": {
        "content_pillar": "expertise_proof",
        "priority": 2,
    },
    "marketing_cases": {
        "content_pillar": "expertise_proof",
        "priority": 2,
    },
}


def normalize_source_item(item: SourceItem) -> SourceNote:
    return SourceNote(
        source_type=item.source_type,
        source_name=item.source_name,
        source_url=item.source_url,
        date_collected=item.collected_at,
        platform=item.source_type.split("_")[0],
        topic_guess=item.content_theme,
        audience_guess=item.audience_segment,
        content_type_guess="video" if item.media_urls else "text",
        engagement_signals=item.engagement_signals,
        raw_text=item.transcript_text,
    )


def build_insight_card(
    note: SourceNote,
    emotional_trigger: str,
    useful_lesson: str,
    narrative_type: str,
    reuse_score: int,
) -> InsightCard:
    theme_hint = SOURCE_THEME_HINTS.get(
        note.topic_guess,
        {"content_pillar": "expertise", "priority": 1},
    )
    return InsightCard(
        audience=note.audience_guess,
        platform=note.platform,
        content_theme=note.topic_guess,
        content_pillar=theme_hint["content_pillar"],
        narrative_type=narrative_type,
        priority=theme_hint["priority"],
        reuse_score=reuse_score,
        emotional_trigger=emotional_trigger,
        useful_lesson=useful_lesson,
    )


def gate_idea_candidate(gates: dict[str, bool]) -> tuple[bool, list[str]]:
    failed = [name for name, passed in gates.items() if not passed]
    return len(failed) == 0, failed


def build_content_brief(
    insight: InsightCard,
    platform: str,
    platform_lane: str,
    funnel_role: str,
    purpose: str,
    hook: str,
    key_points: list[str],
    cta_type: str,
    tone: str,
    length_target: str,
    engagement_objective: str,
    fact_pack: list[str],
    source_rigor: str,
    reference_sources: list[str],
) -> ContentBrief:
    publish_language = "en" if platform_lane == "linkedin_b2b" else "ru"
    return ContentBrief(
        audience=insight.audience,
        platform=platform,
        platform_lane=platform_lane,
        working_language="ru",
        publish_language=publish_language,
        funnel_role=funnel_role,
        purpose=purpose,
        angle=insight.useful_lesson,
        hook=hook,
        key_points=key_points,
        cta_type=cta_type,
        tone=tone,
        length_target=length_target,
        engagement_objective=engagement_objective,
        fact_pack=fact_pack,
        source_rigor=source_rigor,
        reference_sources=reference_sources,
    )
