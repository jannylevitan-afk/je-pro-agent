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
            "## Writer Assignment",
            f"- Writer Assignment ID: wa_{item.item_id}_{decision.platform_lane}",
            f"- Source ID: {item.item_id}",
            f"- Canonical theme: {insight.content_theme}",
            f"- Platform lane: {decision.platform_lane}",
            f"- Publish language: {brief.publish_language}",
            f"- Internal language: {brief.working_language}",
            f"- Primary audience: {insight.audience}",
            f"- Secondary audience: {_secondary_audience(insight)}",
            f"- Funnel role: {brief.funnel_role}",
            f"- Content line: {_content_line(decision.platform_lane)}",
            f"- Strategic priority: {_strategic_priority(decision, insight)}",
            f"- AILLA connection: {_ailla_connection(item, insight, decision)}",
            f"- Expert narrative: {_expert_narrative(insight, decision)}",
            "- Assignment status: approved",
            "",
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
            *_workflow_a_video_context_section(item),
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
            f"- Proof Boundaries: {_proof_boundaries(brief)}",
            "",
            "### Strategy Fit",
            f"- Primary audience portrait: {insight.audience}",
            f"- Optional secondary audience: {_secondary_audience(insight)}",
            f"- Funnel role: {brief.funnel_role}",
            f"- Content line: {_content_line(decision.platform_lane)}",
            f"- Strategic priority: {_strategic_priority(decision, insight)}",
            f"- AILLA connection: {_ailla_connection(item, insight, decision)}",
            f"- Expert narrative: {_expert_narrative(insight, decision)}",
            f"- Why this belongs on this platform: {_platform_fit_reason(decision)}",
            "",
            "### Voice/Register Direction",
            f"- Primary Jane register: {brief.tone}",
            f"- Secondary register, if any: {_secondary_register(decision)}",
            f"- Register reason: {_register_reason(decision)}",
            f"- Rhythm rules: {_rhythm_rules(decision.platform_lane)}",
            f"- Opening style: source-specific first sentence, no separate Hook block",
            "- Ending style: finish as a complete thought; no standalone CTA question",
            "- Tone to avoid: generic AI tone, corporate cliches, fake inspiration, motivational fog",
            "- Forbidden phrases/patterns: Сегодня поговорим о; Давайте разберёмся; В современном мире; Сейчас многие",
            "- Emoji policy: no emoji in LinkedIn; rare/no emoji in professional IG; restrained if lifestyle needs warmth",
            "",
            "### Fact & Privacy Boundaries",
            f"- Allowed public facts: {_allowed_public_facts(item)}",
            f"- Source-backed facts: {'; '.join(brief.fact_pack) or 'source note only'}",
            "- Claims to avoid: invented numbers, invented dates, client names, private deal terms, unsupported ROI claims",
            "- Private/taboo risks: politics, private family details, client identities, closed deal details not marked public",
            "",
            "### Writer Constraints",
            f"- Platform: {brief.platform}",
            f"- Platform lane: {brief.platform_lane}",
            f"- Publish language: {brief.publish_language}",
            f"- Canonical content theme: {insight.content_theme}",
            f"- Required theme lanes: {_required_theme_lanes(insight.content_theme)}",
            f"- This TZ lane: {decision.platform_lane}",
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


def _workflow_a_video_context_section(item: SourceItem) -> list[str]:
    if not _has_video_context(item):
        return []

    raw = item.raw_payload
    first_3_seconds = _raw_text(raw, "first_3_seconds", "opening_visual", "opening_moment")
    source_hook = _raw_text(raw, "source_hook", "detected_hook", "opening_line", "hook")
    first_and_hook = _join_parts([first_3_seconds, f"source hook: {source_hook}" if source_hook else ""])
    comments = _raw_list(raw, "comments_sample", "public_comments", "comments", "reactions")
    return [
        "### Workflow A Video Source Context",
        f"- Video-native source: {'yes' if _has_video_context(item) else 'no'}",
        f"- Video refs: {_join_parts([item.source_url, *item.media_urls]) or item.source_url}",
        f"- Video title: {_raw_text(raw, 'video_title', 'title') or item.source_name}",
        f"- Caption text: {_raw_text(raw, 'caption_text', 'caption', 'description') or _excerpt(item.transcript_text)}",
        f"- Spoken transcript: {_raw_text(raw, 'spoken_transcript', 'transcript', 'video_transcript') or _excerpt(item.transcript_text)}",
        f"- Transcript source: {_raw_text(raw, 'transcript_source') or 'source_text'}",
        f"- Public metrics: {_format_dict(item.engagement_signals) or 'n/a'}",
        f"- Public comments / reactions: {_join_parts(comments) or 'n/a'}",
        f"- First 3 seconds / source hook: {first_and_hook or 'n/a'}",
        f"- Hook pattern: {_raw_text(raw, 'hook_pattern', 'pattern') or 'n/a'}",
        f"- Tension: {_raw_text(raw, 'hook_tension', 'tension') or 'n/a'}",
        f"- Promise: {_raw_text(raw, 'hook_promise', 'promise') or 'n/a'}",
        f"- CTA: {_raw_text(raw, 'hook_cta', 'cta') or 'n/a'}",
        f"- Visual device: {_raw_text(raw, 'visual_device', 'visual_hint', 'visual_hints') or 'n/a'}",
        f"- Repeatable formula: {_raw_text(raw, 'repeatable_formula', 'formula') or 'n/a'}",
        "- Workflow A boundary: video hooks/scripts belong to Workflow A; Writer uses this only as source/evidence context, not as final text hooks or video scripts.",
        "",
    ]


def _excerpt(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _has_video_context(item: SourceItem) -> bool:
    source_type = item.source_type.lower()
    return (
        bool(item.media_urls)
        or item.routing_decision == "both"
        or any(marker in source_type for marker in ("video", "reel", "tiktok", "youtube", "short"))
    )


def _raw_text(raw: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split()).strip()
        if isinstance(value, list):
            for item in value:
                if str(item).strip():
                    return " ".join(str(item).split()).strip()
    return ""


def _raw_list(raw: dict[str, object], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            values.append(" ".join(value.split()).strip())
        elif isinstance(value, list):
            values.extend(" ".join(str(item).split()).strip() for item in value if str(item).strip())
    return _dedupe_text(values)


def _join_parts(parts: list[str]) -> str:
    return "; ".join(part for part in _dedupe_text(parts) if part)


def _dedupe_text(parts: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for part in parts:
        normalized = " ".join(part.split()).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _format_dict(values: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in values.items())


def _secondary_audience(insight: InsightCard) -> str:
    if insight.audience == "developer_investor":
        return "broker / architect_designer when the source supports partner or product logic"
    if insight.audience == "broker":
        return "developer_investor when the source supports market or deal logic"
    if insight.audience == "architect_designer":
        return "developer_investor when design has commercial implications"
    if insight.audience == "lifestyle_expat":
        return "dreamer_woman when the source carries emotional affinity"
    if insight.audience == "dreamer_woman":
        return "lifestyle_expat when the source carries Bali life context"
    return "none"


def _content_line(platform_lane: str) -> str:
    if platform_lane == "instagram_lifestyle":
        return "Instagram lifestyle-led personal brand: founder life, Bali atmosphere, AILLA as lived dream/process"
    if platform_lane == "instagram_professional":
        return "Instagram professional: concrete, visual, saveable Bali real estate / hospitality / product thinking"
    if platform_lane == "linkedin_b2b":
        return "LinkedIn B2B authority: international developer, investor, land-owner, and partner logic"
    return "Workflow B content farm"


def _strategic_priority(decision: WorkflowBDecision, insight: InsightCard) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "B2B trust, strategic partnerships, and market authority"
    if decision.platform_lane == "instagram_professional":
        return "saveable expertise, deal literacy, and expert positioning"
    if insight.content_theme in {"founder_journey", "bali_travel", "wellness_architecture"}:
        return "emotional affinity and personal brand depth"
    return "audience fit and reusable insight"


def _ailla_connection(
    item: SourceItem,
    insight: InsightCard,
    decision: WorkflowBDecision,
) -> str:
    text = f"{item.transcript_text} {insight.useful_lesson}".lower()
    if "ailla" not in text and insight.content_theme != "wellness_architecture":
        return "Do not force AILLA; mention only if source material supports the bridge."
    if decision.platform_lane == "instagram_lifestyle":
        return "Use AILLA emotionally as lived transformation, process, and atmosphere."
    if decision.platform_lane == "instagram_professional":
        return "Use AILLA rationally as product thinking, not decor."
    return "Use AILLA as an experience-development case only when source-backed."


def _expert_narrative(insight: InsightCard, decision: WorkflowBDecision) -> str:
    if insight.content_theme == "market_reports":
        return "market red flags, dumping, overlaunching, timing, and downside protection"
    if insight.content_theme == "land_and_legal":
        return "legal structure, land quality, rights, and pre-deal risk"
    if insight.content_theme == "expert_pain_bali":
        return "Bali-specific deal friction, buyer pain, and operational reality"
    if insight.content_theme == "global_trends":
        return "global travel/wellness behavior translated into Bali positioning"
    if insight.content_theme == "boutique_hotels":
        return "hospitality positioning, operations, guest experience, and yield logic"
    if insight.content_theme == "marketing_cases":
        return "commercial signal over noisy marketing activity"
    if decision.platform_lane == "instagram_lifestyle":
        return "personal brand affinity without turning lifestyle into a hidden funnel"
    return "source-backed product and market logic"


def _platform_fit_reason(decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "The lane needs international B2B authority, not lifestyle translation."
    if decision.platform_lane == "instagram_professional":
        return "The lane turns expert insight into concrete, saveable Instagram content."
    return "The lane builds recognition, emotional affinity, and lived context around the founder brand."


def _secondary_register(decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "register_3 when a personal scene clarifies the market point"
    if decision.platform_lane == "instagram_professional":
        return "register_6 when the post needs manifesto/product clarity"
    if decision.platform_lane == "instagram_lifestyle":
        return "register_9 when family/home/project objects support the source"
    return "none"


def _register_reason(decision: WorkflowBDecision) -> str:
    if decision.tone == "register_3":
        return "cold analytics with a human scene keeps the expert point readable"
    if decision.tone == "register_4":
        return "geo-economic facts make the risk and market logic credible"
    if decision.tone == "register_6":
        return "corporate manifesto fits AILLA, product philosophy, and developer trust"
    if decision.tone == "register_7":
        return "emotional exhale fits founder-life material without fake inspiration"
    if decision.tone == "register_2":
        return "object as transformation lens fits Bali, wellness, and lived design"
    return "selected by canonical theme and platform lane"


def _rhythm_rules(platform_lane: str) -> str:
    if platform_lane == "linkedin_b2b":
        return "clear short paragraphs, one strategic claim per paragraph, no lifestyle detour"
    if platform_lane == "instagram_professional":
        return "sharp first line, visual example, saveable insight, no report-like bulk"
    return "alive, intimate, concrete scenes; avoid syrupy inspiration"


def _proof_boundaries(brief: ContentBrief) -> str:
    if brief.source_rigor == "market-critical":
        return "market/legal claims require source references or must be softened"
    if brief.source_rigor == "expert":
        return "expert claims require source note, fact pack, or references"
    return "standard source note is enough; do not add unsupported metrics"


def _allowed_public_facts(item: SourceItem) -> str:
    raw = item.raw_payload.get("allowed_public_facts")
    if isinstance(raw, list):
        facts = [str(fact).strip() for fact in raw if str(fact).strip()]
        if facts:
            return "; ".join(facts[:5])
    return "Jane/Clear/AILLA facts only if present in source note, Fact Dossier, or approved fact pack"


def _required_theme_lanes(content_theme: str) -> str:
    if content_theme in {"founder_journey", "bali_travel"}:
        return "instagram_lifestyle"
    if content_theme == "wellness_architecture":
        return "instagram_lifestyle, instagram_professional, linkedin_b2b"
    return "instagram_professional, linkedin_b2b"
