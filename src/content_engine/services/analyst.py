from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from content_engine.context.workflow_b_rules import WorkflowBDecision, expand_workflow_b_decisions
from content_engine.llm.analyst import InsightExtractionResult
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import (
    ContentBrief,
    IdeaCandidate,
    InsightCard,
    SourceNote,
)
from content_engine.services.workflow_b import (
    SOURCE_THEME_HINTS,
    build_content_brief,
    build_idea_candidate,
    normalize_source_item,
)


class WorkflowAnalyst(Protocol):
    def extract_insight(self, item: SourceItem) -> InsightExtractionResult:
        ...


_KNOWN_THEMES = set(SOURCE_THEME_HINTS)
_KNOWN_AUDIENCES = {
    "developer_investor",
    "broker",
    "architect_designer",
    "lifestyle_expat",
    "dreamer_woman",
}


@dataclass(frozen=True, slots=True)
class WriterSpec:
    """Complete TZ (task specification) for the Writer entity — one spec per platform lane."""

    decision: WorkflowBDecision
    idea: IdeaCandidate
    brief: ContentBrief
    writer_tz: str


@dataclass(frozen=True, slots=True)
class AnalystReport:
    """Full analyst output: Phase 1 structure + Phase 2 insight + per-lane Writer specs."""

    source_item_id: str
    source_note: SourceNote
    insight: InsightCard
    writer_specs: list[WriterSpec]
    preflight_passed: bool
    risk_flags: list[str]


def run_analyst(
    item: SourceItem,
    analyst: WorkflowAnalyst,
    verified_facts: set[str] | None = None,
) -> AnalystReport:
    """
    Phase 1: normalize and deduplicate.
    Phase 2: AI-powered insight extraction.
    Output: AnalystReport with per-lane WriterSpecs ready for the Writer entity.
    """
    risk_flags = _preflight_check(item)

    note = normalize_source_item(item)

    extraction = analyst.extract_insight(item)
    theme_hint = SOURCE_THEME_HINTS.get(
        item.content_theme,
        {"content_pillar": "expertise", "priority": 1},
    )
    platform = item.source_type.split("_")[0]
    insight = InsightCard(
        audience=item.audience_segment,
        platform=platform,
        topic=extraction.topic or item.content_theme.replace("_", " "),
        angle=extraction.angle or extraction.useful_lesson,
        audience_fit=extraction.audience_fit or f"{item.audience_segment} needs this source to make a better content decision.",
        content_theme=item.content_theme,
        content_pillar=theme_hint["content_pillar"],
        narrative_type=extraction.narrative_type,
        priority=theme_hint["priority"],
        reuse_score=extraction.reuse_score,
        emotional_trigger=extraction.emotional_trigger,
        useful_lesson=extraction.useful_lesson,
    )

    decisions = expand_workflow_b_decisions(item)
    writer_specs = [
        _build_writer_spec(insight, decision, item, extraction, verified_facts or set())
        for decision in decisions
    ]

    return AnalystReport(
        source_item_id=item.item_id,
        source_note=note,
        insight=insight,
        writer_specs=writer_specs,
        preflight_passed=len(risk_flags) == 0,
        risk_flags=risk_flags,
    )


def run_analyst_batch(
    items: list[SourceItem],
    analyst: WorkflowAnalyst,
    verified_facts: set[str] | None = None,
) -> list[AnalystReport]:
    return [
        run_analyst(item, analyst, verified_facts=verified_facts)
        for item in dedupe_source_items(items)
    ]


def dedupe_source_items(items: list[SourceItem]) -> list[SourceItem]:
    selected: dict[str, SourceItem] = {}
    for item in items:
        existing = selected.get(item.dedupe_key)
        if existing is None or _source_item_rank(item) > _source_item_rank(existing):
            selected[item.dedupe_key] = item
    return list(selected.values())


def _build_writer_spec(
    insight: InsightCard,
    decision: WorkflowBDecision,
    item: SourceItem,
    extraction: InsightExtractionResult,
    verified_facts: set[str],
) -> WriterSpec:
    idea = build_idea_candidate(
        insight=insight,
        platform=decision.platform,
        platform_lane=decision.platform_lane,
        language_mode="ru",
        funnel_role=decision.funnel_role,
        working_title=f"{insight.content_theme.replace('_', ' ').title()} — {decision.platform_lane}",
        emotional_hook=decision.emotional_hook,
        desired_reaction=decision.desired_reaction,
        suggested_format=_suggested_format(decision),
    )

    brief = build_content_brief(
        insight=insight,
        platform=decision.platform,
        platform_lane=decision.platform_lane,
        funnel_role=decision.funnel_role,
        purpose=_purpose(decision),
        hook=_hook_line(decision),
        key_points=_key_points(insight),
        cta_type=decision.cta_type,
        tone=decision.tone,
        length_target="medium",
        engagement_objective=decision.engagement_objective,
        fact_pack=_matching_fact_pack(item, verified_facts),
        source_rigor=decision.source_rigor,
        reference_sources=_reference_sources(item, decision),
    )
    writer_tz = _format_writer_tz(
        item=item,
        insight=insight,
        decision=decision,
        extraction=extraction,
        brief=brief,
    )
    brief = brief.model_copy(update={"analyst_tz": writer_tz})

    return WriterSpec(
        decision=decision,
        idea=idea,
        brief=brief,
        writer_tz=writer_tz,
    )


def _preflight_check(item: SourceItem) -> list[str]:
    flags: list[str] = []
    if not item.transcript_text.strip():
        flags.append("transcript_text is empty — no source material to analyse")
    if item.audience_segment not in _KNOWN_AUDIENCES:
        flags.append(f"unknown audience_segment: {item.audience_segment!r}")
    if item.content_theme not in _KNOWN_THEMES:
        flags.append(f"unknown content_theme: {item.content_theme!r}")
    if item.routing_decision not in {"workflow_a", "workflow_b", "both"}:
        flags.append(f"unexpected routing_decision: {item.routing_decision!r}")
    return flags


def _source_item_rank(item: SourceItem) -> tuple[float, int, int]:
    return (
        item.routing_confidence,
        max(item.engagement_signals.values(), default=0),
        len(item.transcript_text.split()),
    )


def _suggested_format(decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "thought_leadership_post"
    if decision.platform_lane == "instagram_lifestyle":
        return "story_caption"
    return "carousel_caption"


def _purpose(decision: WorkflowBDecision) -> str:
    if decision.funnel_role == "affinity":
        return "Create emotional closeness and recognition."
    if decision.funnel_role == "authority":
        return "Build market trust through concrete insight."
    return "Trigger a meaningful next-step reaction."


def _hook_line(decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "The cheapest line item in Bali is often the most expensive strategic mistake."
    if decision.platform_lane == "instagram_lifestyle":
        return "Some projects change your mood before they change your spreadsheet."
    return "What looks cheap first is often the most expensive later."


def _key_points(insight: InsightCard) -> list[str]:
    return [
        insight.useful_lesson.rstrip("."),
        insight.angle.rstrip(".") if insight.angle else "Use the extracted angle before writing.",
        insight.audience_fit.rstrip(".") if insight.audience_fit else "Keep the audience fit visible.",
        "Legal structure changes the deal far more than brochure language suggests.",
        "Operations and positioning shape the real outcome after purchase.",
    ][:4]


def _reference_sources(item: SourceItem, decision: WorkflowBDecision) -> list[str]:
    raw = item.raw_payload.get("reference_sources")
    if isinstance(raw, list):
        sources = [str(s) for s in raw if str(s).strip()]
        if decision.source_rigor == "market-critical":
            return sources[:4] if len(sources) >= 4 else _fallback_sources(item, 4)
        if decision.source_rigor == "expert":
            return sources[:3] if len(sources) >= 3 else _fallback_sources(item, 3)
        return sources[:1]
    if decision.source_rigor == "market-critical":
        return _fallback_sources(item, 4)
    if decision.source_rigor == "expert":
        return _fallback_sources(item, 3)
    return []


def _fallback_sources(item: SourceItem, count: int) -> list[str]:
    suffixes = ["source", "context", "ops", "market", "evidence"]
    return [f"{item.source_url}#{suffixes[i]}" for i in range(count)]


def _matching_fact_pack(item: SourceItem, verified_facts: set[str]) -> list[str]:
    text = item.transcript_text.lower()
    return [
        fact
        for fact in sorted(verified_facts)
        if sum(1 for token in fact.lower().split() if len(token) > 4 and token in text) >= 1
    ][:5]


def _format_writer_tz(
    *,
    item: SourceItem,
    insight: InsightCard,
    decision: WorkflowBDecision,
    extraction: InsightExtractionResult,
    brief: ContentBrief,
) -> str:
    return "\n".join(
        [
            "## Writer Entity TZ",
            "",
            "### Phase 1 Source Note",
            f"- Source ID: {item.item_id}",
            f"- Source URL: {item.source_url}",
            f"- Platform: {brief.platform_lane}",
            f"- Audience: {insight.audience}",
            f"- Content theme: {insight.content_theme}",
            f"- Raw excerpt: {_excerpt(item.transcript_text)}",
            "",
            "### Phase 2 Insight Card",
            f"- Topic: {insight.topic}",
            f"- Angle: {insight.angle}",
            f"- Emotional Trigger: {insight.emotional_trigger}",
            f"- Audience Fit: {insight.audience_fit}",
            f"- Useful Lesson: {insight.useful_lesson}",
            f"- Narrative Type: {insight.narrative_type}",
            f"- Reuse Score: {insight.reuse_score}/5",
            f"- Confidence: {extraction.confidence_score:.2f}",
            "",
            "### Marketing Research Adaptation",
            f"- JTBD / Customer Job: {extraction.customer_job or 'infer from source without inventing facts'}",
            f"- Pain Point: {extraction.pain_point or 'use only source-backed pain'}",
            f"- Trigger Event: {extraction.trigger_event or 'source event or monitoring signal'}",
            f"- Desired Outcome: {extraction.desired_outcome or decision.desired_reaction}",
            f"- Behavioral Trigger: {extraction.behavioral_trigger or 'direct_benefit'}",
            "",
            "### Writer Constraints",
            f"- Purpose: {brief.purpose}",
            f"- Tone/Register: {brief.tone}",
            f"- Format: {_suggested_format(decision)}",
            f"- Opening guide: {brief.hook}",
            f"- Key points: {'; '.join(brief.key_points)}",
            f"- Facts allowed: {'; '.join(brief.fact_pack) or 'source_note only'}",
            f"- Reference sources: {'; '.join(brief.reference_sources) or item.source_url}",
            "- Do not write from raw topic alone; write from this insight and source note.",
            "",
            "### Opening Sentence Guardrails",
            "- The first line of Final Text is the opening_sentence; do not output a separate Hook block.",
            "- Keep it 5-14 words, concrete, source-specific, and understandable without context.",
            "- It must create tension, recognition, a useful problem, or a precise conflict for the stated audience.",
            "- Do not use tautological openings: no repeated same-root adjective/noun loops such as cheap/cheap, risk/risky, or дешёвый/дешево.",
            "- Banned weak examples: Дешёвый вход на Бали..., Дешёвый риск почти никогда не выглядит дешево, Cheap risk rarely looks cheap.",
            "- If an opening can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.",
            "- Do not end Final Text with a standalone CTA question; keep review-facing output as final text only.",
            "",
            "### Required Output Format",
            "```markdown",
            "## Final Content Asset",
            "**Content ID:**",
            "**Title:**",
            "**Platform:**",
            "**Pillar:**",
            "**Format:**",
            "**Approval Status:**",
            "",
            "### Final Text",
            "...",
            "```",
            "- Do not output Hook, CTA, Traceability, or QA sections in the final asset.",
        ]
    )


def _excerpt(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"
