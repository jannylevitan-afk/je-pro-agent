from typing import TypedDict

from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import (
    ContentBrief,
    FunnelRole,
    IdeaCandidate,
    InsightCard,
    Language,
    LengthTarget,
    Platform,
    PlatformLane,
    SourceNote,
    SourceRigor,
)


class _ThemeHint(TypedDict):
    content_pillar: str
    priority: int


SOURCE_THEME_HINTS: dict[str, _ThemeHint] = {
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


def build_idea_candidate(
    insight: InsightCard,
    platform: Platform,
    platform_lane: PlatformLane,
    language_mode: Language,
    funnel_role: FunnelRole,
    working_title: str,
    emotional_hook: str,
    desired_reaction: str,
    suggested_format: str,
) -> IdeaCandidate:
    return IdeaCandidate(
        working_title=working_title,
        target_platform=platform,
        platform_lane=platform_lane,
        language_mode=language_mode,
        funnel_role=funnel_role,
        target_audience=insight.audience,
        content_pillar=insight.content_pillar,
        emotional_hook=emotional_hook,
        useful_point=insight.useful_lesson,
        desired_reaction=desired_reaction,
        suggested_format=suggested_format,
    )


def gate_idea_candidate(gates: dict[str, bool]) -> tuple[bool, list[str]]:
    failed = [name for name, passed in gates.items() if not passed]
    return len(failed) == 0, failed


def build_content_brief(
    insight: InsightCard,
    platform: Platform,
    platform_lane: PlatformLane,
    funnel_role: FunnelRole,
    purpose: str,
    hook: str,
    key_points: list[str],
    cta_type: str,
    tone: str,
    length_target: LengthTarget,
    engagement_objective: str,
    fact_pack: list[str],
    source_rigor: SourceRigor,
    reference_sources: list[str],
) -> ContentBrief:
    publish_language: Language = "en" if platform_lane == "linkedin_b2b" else "ru"
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
