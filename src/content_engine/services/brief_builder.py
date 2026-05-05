from __future__ import annotations

from content_engine.models.brief_builder import BriefBuilderResult, WorkflowABrief, WorkflowBBrief
from content_engine.models.hook_research import (
    ApprovedWorkflowAHandoff,
    HookOpportunity,
    HookResearchOutcomeBoard,
    is_workflow_a_eligible_hook,
)
from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import ApprovedOpportunity, ProducerDecision, SceneCard


def build_briefs(
    approved_items: list[ApprovedOpportunity],
    *,
    opportunities: list[OpportunityCandidate],
    decisions: list[ProducerDecision],
    scenes: list[SceneCard] | None = None,
    created_at: str,
) -> list[BriefBuilderResult]:
    opportunities_by_id = {opportunity.opportunity_id: opportunity for opportunity in opportunities}
    decisions_by_id = {decision.decision_id: decision for decision in decisions}
    scenes_by_id = {scene.scene_id: scene for scene in scenes or []}
    return [
        build_brief(
            approved=approved,
            opportunity=opportunities_by_id[approved.opportunity_id],
            decision=decisions_by_id[approved.decision_id],
            scene=_scene_for_approved(approved, decisions_by_id[approved.decision_id], scenes_by_id),
            created_at=created_at,
        )
        for approved in approved_items
    ]


def build_brief(
    *,
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
    scene: SceneCard | None = None,
    created_at: str = "2026-04-29T00:00:00+08:00",
) -> BriefBuilderResult:
    _validate_alignment(approved, opportunity, decision, scene)
    brief: WorkflowABrief | WorkflowBBrief
    if approved.selected_workflow == "workflow_a":
        brief = _build_workflow_a_brief(approved, opportunity, decision, scene)
    else:
        brief = _build_workflow_b_brief(approved, opportunity, decision, scene)
    return BriefBuilderResult(
        approved_id=approved.approved_id,
        brief=brief,
        created_at=created_at,
    )


def build_workflow_a_briefs_from_hook_board(
    board: HookResearchOutcomeBoard,
    *,
    created_at: str,
) -> list[BriefBuilderResult]:
    """Convert approved hook research handoffs into Workflow A briefs.

    Brief Builder is the only layer allowed to perform this conversion, and it
    only accepts rows approved by a human/producer with QA PASS and acceptable
    risk.
    """

    hooks_by_id = {hook.hook_id: hook for hook in board.hook_opportunities}
    results: list[BriefBuilderResult] = []
    for handoff in board.approved_for_workflow_a:
        hook = hooks_by_id.get(handoff.approved_hook_id)
        if hook is None:
            raise ValueError(f"approved hook {handoff.approved_hook_id} is missing from HookResearchOutcomeBoard")
        if not is_workflow_a_eligible_hook(hook):
            raise ValueError("Only APPROVE_FOR_WORKFLOW_A + QA PASS + acceptable risk hooks can become WorkflowABrief")
        brief = _workflow_a_brief_from_hook_handoff(board, handoff, hook)
        results.append(
            BriefBuilderResult(
                approved_id=handoff.approved_opportunity_id,
                brief=brief,
                created_at=created_at,
            )
        )
    return results


def _build_workflow_b_brief(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
    scene: SceneCard | None,
) -> WorkflowBBrief:
    selected_platform = approved.selected_platform
    return WorkflowBBrief(
        brief_id=_brief_id(approved),
        source_item_id=approved.source_item_id,
        opportunity_id=approved.opportunity_id,
        decision_id=approved.decision_id,
        workflow="workflow_b",
        selected_platform=selected_platform,
        rubric=opportunity.rubric,
        audience_segment=opportunity.audience_segment,
        production_intent=approved.production_intent,
        core_idea=approved.core_idea,
        angle=opportunity.topic,
        emotional_trigger=opportunity.emotional_trigger,
        source_summary=_source_summary(opportunity),
        source_text_excerpt=opportunity.core_idea,
        what_performed=opportunity.what_performed,
        jane_adaptation_instruction=approved.jane_adaptation_brief,
        factual_boundaries=_factual_boundaries(approved, opportunity, decision),
        must_include=_workflow_b_must_include(approved, opportunity, scene),
        must_not_include=_workflow_b_must_not_include(),
        tone_rules=_tone_rules(opportunity),
        opening_direction=_opening_direction(opportunity),
        quality_criteria=_quality_criteria(opportunity),
        risk_flags=_risk_flags(approved, opportunity),
        season_id=approved.season_id,
        episode_id=approved.episode_id,
        scene_id=approved.scene_id,
        producer_scene_type=_producer_scene_type(scene),
        producer_plot_function=_producer_plot_function(scene),
        producer_sales_intensity=_producer_sales_intensity(scene),
        producer_scene_hook=_producer_scene_hook(scene),
        producer_cta_or_next_hook=_producer_cta_or_next_hook(scene),
        publish_language="en" if selected_platform == "linkedin" else "ru",
        internal_working_language="ru",
        platform_variants=[],
    )


def _workflow_a_brief_from_hook_handoff(
    board: HookResearchOutcomeBoard,
    handoff: ApprovedWorkflowAHandoff,
    hook: HookOpportunity,
) -> WorkflowABrief:
    platform = _platform_from_hook_handoff(handoff, hook)
    source_item_id = _source_item_id_from_handoff(handoff, hook)
    return WorkflowABrief(
        brief_id=f"brief_{handoff.approved_opportunity_id}",
        source_item_id=source_item_id,
        opportunity_id=handoff.approved_opportunity_id,
        decision_id=handoff.directive_id,
        workflow="workflow_a",
        selected_platform=platform,
        rubric=str(handoff.producer_context.get("content_line") or hook.content_line),
        audience_segment=str(handoff.producer_context.get("target_audience") or hook.target_audience),
        production_intent=f"Create Workflow A video from approved hook {handoff.approved_hook_id}.",
        core_idea=handoff.video_angle,
        angle=handoff.video_angle,
        emotional_trigger=hook.emotional_trigger,
        source_summary=_hook_source_summary(board, handoff, hook),
        source_text_excerpt=handoff.selected_hook,
        what_performed=str(handoff.source_context.get("why_it_performed") or hook.why_it_performed),
        jane_adaptation_instruction=handoff.reuse_boundary,
        factual_boundaries=_unique(
            [
                *handoff.factual_boundaries,
                *[f"Evidence ref: {ref}" for ref in handoff.evidence_refs],
                "Research Agent already completed hook research; Workflow A must use this brief only.",
            ]
        ),
        must_include=[
            "selected hook",
            handoff.selected_hook,
            f"first frame text: {handoff.first_frame_text}",
            f"video angle: {handoff.video_angle}",
            f"CTA direction: {handoff.cta_direction}",
            "editorial QA before HumanReviewAsset",
        ],
        must_not_include=[
            "new research",
            "source discovery",
            "publish queue",
            "scheduled publishing",
            "publisher assignment",
            "platform variants",
            "final platform captions",
        ],
        tone_rules=[
            "Jane voice: lived expertise, concrete, no generic AI tone.",
            str(hook.tone_direction),
        ],
        opening_direction=handoff.selected_hook,
        quality_criteria=[
            "board-gated",
            "QA PASS hook only",
            "acceptable risk only",
            "source-backed pattern adaptation",
            "script uses WorkflowABrief only",
        ],
        risk_flags=[hook.risk_notes] if hook.risk_notes else [],
        season_id=handoff.season_id,
        episode_id=handoff.episode_id,
        scene_id=handoff.scene_id,
        producer_scene_type=_optional_str(handoff.producer_context.get("scene_type")),
        producer_plot_function=_optional_str(handoff.producer_context.get("plot_function")),
        producer_sales_intensity=_producer_sales_intensity_from_label(handoff.producer_context.get("sales_intensity")),
        producer_scene_hook=handoff.selected_hook,
        producer_cta_or_next_hook=handoff.cta_direction,
        video_refs=_video_refs_from_hook_handoff(handoff),
        source_hook=handoff.selected_hook,
        transcript_source="HookResearchOutcomeBoard / ApprovedWorkflowAHandoff",
        hook_board_id=board.board_header.board_id,
        approved_hook_id=handoff.approved_hook_id,
        first_frame_text=handoff.first_frame_text,
        cta_direction=handoff.cta_direction,
        visual_opening_direction=hook.visual_opening_direction,
        hook_research_evidence_refs=list(handoff.evidence_refs),
    )


def _build_workflow_a_brief(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
    scene: SceneCard | None,
) -> WorkflowABrief:
    return WorkflowABrief(
        brief_id=_brief_id(approved),
        source_item_id=approved.source_item_id,
        opportunity_id=approved.opportunity_id,
        decision_id=approved.decision_id,
        workflow="workflow_a",
        selected_platform=approved.selected_platform,
        rubric=opportunity.rubric,
        audience_segment=opportunity.audience_segment,
        production_intent=approved.production_intent,
        core_idea=approved.core_idea,
        angle=opportunity.topic,
        emotional_trigger=opportunity.emotional_trigger,
        source_summary=_source_summary(opportunity),
        source_text_excerpt=opportunity.core_idea,
        what_performed=opportunity.what_performed,
        jane_adaptation_instruction=approved.jane_adaptation_brief,
        factual_boundaries=_factual_boundaries(approved, opportunity, decision),
        must_include=_workflow_a_must_include(scene),
        must_not_include=[
            "publish queue",
            "scheduled publishing",
            "publisher assignment",
            "platform variants",
            "visual generation instructions",
        ],
        tone_rules=_tone_rules(opportunity),
        opening_direction="Use the source hook when available; otherwise keep first seconds concrete and visual.",
        quality_criteria=[
            "video-native",
            "source hook preserved when available",
            "script uses source-backed material only",
        ],
        risk_flags=_risk_flags(approved, opportunity),
        season_id=approved.season_id,
        episode_id=approved.episode_id,
        scene_id=approved.scene_id,
        producer_scene_type=_producer_scene_type(scene),
        producer_plot_function=_producer_plot_function(scene),
        producer_sales_intensity=_producer_sales_intensity(scene),
        producer_scene_hook=_producer_scene_hook(scene),
        producer_cta_or_next_hook=_producer_cta_or_next_hook(scene),
        video_refs=[opportunity.source_url],
        source_hook=opportunity.topic,
        transcript_source="SourceItem / Analyst OpportunityCandidate",
    )


def _validate_alignment(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
    scene: SceneCard | None,
) -> None:
    if approved.opportunity_id != opportunity.opportunity_id:
        raise ValueError("approved opportunity_id must match OpportunityCandidate opportunity_id")
    if approved.decision_id != decision.decision_id:
        raise ValueError("approved decision_id must match ProducerDecision decision_id")
    if approved.source_item_id != opportunity.source_item_id or approved.source_item_id != decision.source_item_id:
        raise ValueError("source_item_id must match across approved opportunity, candidate, and decision")
    if decision.decision != "approve":
        raise ValueError("Brief Builder only accepts approved ProducerDecision")
    if approved.selected_workflow != decision.selected_workflow:
        raise ValueError("approved selected_workflow must match ProducerDecision selected_workflow")
    if approved.selected_platform != decision.selected_platform:
        raise ValueError("approved selected_platform must match ProducerDecision selected_platform")
    _validate_optional_id_match("season_id", approved.season_id, decision.season_id)
    _validate_optional_id_match("episode_id", approved.episode_id, decision.episode_id)
    _validate_optional_id_match("scene_id", approved.scene_id, decision.scene_id)
    if scene:
        _validate_scene_match(approved, decision, scene)


def _brief_id(approved: ApprovedOpportunity) -> str:
    return f"brief_{approved.approved_id}"


def _source_summary(opportunity: OpportunityCandidate) -> str:
    return (
        f"{opportunity.source_name} / {opportunity.source_type}: {opportunity.topic}. "
        f"Popularity: {opportunity.popularity_label}. Metrics: {opportunity.public_metrics}."
    )


def _factual_boundaries(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
) -> list[str]:
    boundaries = [
        "Use only the supplied SourceItem, OpportunityCandidate, and ProducerDecision evidence.",
        "Do not invent laws, prices, dates, cases, revenue, client names, or private details.",
        "Preserve source URL and evidence refs internally.",
        *[f"Evidence ref: {ref}" for ref in approved.evidence_refs],
    ]
    boundaries.extend(decision.constraints)
    boundaries.extend(opportunity.risk_flags)
    return _unique(boundaries)


def _workflow_b_must_include(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
    scene: SceneCard | None,
) -> list[str]:
    required = [
        approved.core_idea,
        opportunity.what_performed,
        "one thought / one emotion / one plot",
        "Jane-specific adaptation, not copied source text",
        "a concrete opening sentence inside Final Text",
    ]
    if scene:
        required.extend(
            [
                f"Producer scene function: {scene.scene_type} / {scene.plot_function} / intensity {scene.sales_intensity}",
                "Use producer hook as scene direction, not as a separate Hook block.",
                "Use producer CTA/next hook only as direction inside the final text, not as a standalone CTA section.",
            ]
        )
    return required


def _workflow_a_must_include(scene: SceneCard | None) -> list[str]:
    required = [
        "selected hook",
        "spoken script",
        "filming card",
        "source URL and public metrics context",
    ]
    if scene:
        required.extend(
            [
                f"Producer scene function: {scene.scene_type} / {scene.plot_function} / intensity {scene.sales_intensity}",
                "Use producer hook/CTA direction to shape the video arc without inventing proof.",
            ]
        )
    return required


def _workflow_b_must_not_include() -> list[str]:
    return [
        "separate Hook block",
        "standalone CTA question",
        "Traceability block in user-facing output",
        "QA block in user-facing output",
        "platform variants",
        "publish queue",
        "scheduler or publisher fields",
        "generic AI intro",
    ]


def _tone_rules(opportunity: OpportunityCandidate) -> list[str]:
    rules = [
        "Jane voice: lived expertise, concrete, no generic AI tone.",
        f"Audience: {opportunity.audience_segment}.",
        f"Rubric: {opportunity.rubric}.",
    ]
    if opportunity.suggested_platform == "linkedin":
        rules.append("LinkedIn final text is English; internal working master remains Russian.")
    return rules


def _opening_direction(opportunity: OpportunityCandidate) -> str:
    if opportunity.emotional_trigger in {"fear", "страх"}:
        return "Start with a short warning that names the hidden cost without clickbait."
    if opportunity.emotional_trigger in {"curiosity", "любопытство"}:
        return "Start with a specific curiosity gap tied to the source."
    return "Start with a concrete, source-specific sentence; no polite intro."


def _quality_criteria(opportunity: OpportunityCandidate) -> list[str]:
    return [
        "source-backed",
        "rubric fit",
        "audience fit",
        "1 thought / 1 emotion / 1 plot",
        "no unsupported claims",
        f"risk level respected: {opportunity.risk_level}",
    ]


def _risk_flags(
    approved: ApprovedOpportunity,
    opportunity: OpportunityCandidate,
) -> list[str]:
    return _unique([*approved.risk_flags, *opportunity.risk_flags])


def _scene_for_approved(
    approved: ApprovedOpportunity,
    decision: ProducerDecision,
    scenes_by_id: dict[str, SceneCard],
) -> SceneCard | None:
    scene_id = approved.scene_id or decision.scene_id
    if not scene_id:
        return None
    return scenes_by_id.get(scene_id)


def _validate_optional_id_match(field_name: str, left: str | None, right: str | None) -> None:
    if left and right and left != right:
        raise ValueError(f"approved {field_name} must match ProducerDecision {field_name}")


def _validate_scene_match(
    approved: ApprovedOpportunity,
    decision: ProducerDecision,
    scene: SceneCard,
) -> None:
    expected_scene_id = approved.scene_id or decision.scene_id
    if expected_scene_id and scene.scene_id != expected_scene_id:
        raise ValueError("scene_id must match approved opportunity or ProducerDecision scene_id")
    expected_episode_id = approved.episode_id or decision.episode_id
    if expected_episode_id and scene.episode_id != expected_episode_id:
        raise ValueError("episode_id must match approved opportunity or ProducerDecision episode_id")


def _producer_scene_type(scene: SceneCard | None) -> str | None:
    return scene.scene_type if scene else None


def _producer_plot_function(scene: SceneCard | None) -> str | None:
    return scene.plot_function if scene else None


def _producer_sales_intensity(scene: SceneCard | None) -> int | None:
    return scene.sales_intensity if scene else None


def _producer_scene_hook(scene: SceneCard | None) -> str | None:
    return scene.hook if scene else None


def _producer_cta_or_next_hook(scene: SceneCard | None) -> str | None:
    if not scene:
        return None
    return scene.cta or scene.next_hook


def _platform_from_hook_handoff(
    handoff: ApprovedWorkflowAHandoff,
    hook: HookOpportunity,
) -> str:
    platform = str(handoff.source_context.get("source_platform") or hook.source_platform or "instagram").lower()
    if "tiktok" in platform:
        return "tiktok"
    if "youtube" in platform or "short" in platform:
        return "youtube"
    if "linkedin" in platform:
        return "linkedin"
    return "instagram"


def _source_item_id_from_handoff(
    handoff: ApprovedWorkflowAHandoff,
    hook: HookOpportunity,
) -> str:
    source_refs = handoff.source_context.get("source_item_refs")
    if isinstance(source_refs, list):
        for source_ref in source_refs:
            if isinstance(source_ref, str) and source_ref.strip():
                return source_ref
    if hook.source_item_refs:
        return hook.source_item_refs[0]
    return handoff.approved_hook_id


def _video_refs_from_hook_handoff(handoff: ApprovedWorkflowAHandoff) -> list[str]:
    refs: list[str] = []
    source_video_url = handoff.source_context.get("source_video_url")
    if isinstance(source_video_url, str) and source_video_url.startswith(("http://", "https://")):
        refs.append(source_video_url)
    for evidence_ref in handoff.evidence_refs:
        if evidence_ref.startswith(("http://", "https://")) and evidence_ref not in refs:
            refs.append(evidence_ref)
    return refs


def _hook_source_summary(
    board: HookResearchOutcomeBoard,
    handoff: ApprovedWorkflowAHandoff,
    hook: HookOpportunity,
) -> str:
    evidence_summary = ", ".join(handoff.evidence_refs) if handoff.evidence_refs else "producer original"
    return (
        f"{board.board_header.board_type} {board.board_header.board_id}; "
        f"mode: {hook.input_mode}; source evidence: {evidence_summary}; "
        f"signal: {handoff.source_context.get('performance_signal') or hook.performance_signal or 'producer strategy'}."
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _producer_sales_intensity_from_label(value: object) -> int | None:
    label = str(value or "").strip().lower()
    mapping = {
        "none": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
    }
    return mapping.get(label)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(normalized)
    return unique_values


__all__ = ["build_brief", "build_briefs", "build_workflow_a_briefs_from_hook_board"]
