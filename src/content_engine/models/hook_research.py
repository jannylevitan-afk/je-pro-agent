from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


WorkflowRoute = Literal["workflow_a"]
InputMode = Literal["RESEARCH_MINED", "PRODUCER_ORIGINAL"]
BoardStatus = Literal[
    "DRAFT",
    "BLOCKED",
    "READY_FOR_RESEARCH",
    "RESEARCH_RUNNING",
    "READY_FOR_ANALYST_REVIEW",
    "READY_FOR_PRODUCER_REVIEW",
    "PARTIALLY_APPROVED",
    "APPROVED_FOR_WORKFLOW_A",
    "NEEDS_REWORK",
    "ARCHIVED",
]
DecisionStatus = Literal["NEW", "SHORTLISTED", "APPROVED", "BACKUP", "REQUEST_REWRITE", "HOLD", "REJECTED"]
HumanDecision = Literal[
    "APPROVE_FOR_WORKFLOW_A",
    "BACKUP",
    "REQUEST_REWRITE",
    "HOLD",
    "REJECT",
    "SEND_TO_WORKFLOW_B",
]
RiskLevel = Literal["none", "low", "medium", "high", "blocker"]
QAStatus = Literal["PASS", "NEEDS_REWRITE", "FAIL", "BLOCKED"]
BlockedReason = Literal["PRODUCER_HOOK_SEARCH_TASK_MISSING", "PRODUCER_HOOK_SEARCH_TASK_INVALID"]


class HookResearchBlockedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["BLOCKED"] = "BLOCKED"
    blocked_reason: BlockedReason
    message: str


class BoardHeader(BaseModel):
    model_config = ConfigDict(extra="forbid")

    board_id: str = Field(min_length=1)
    board_type: Literal["HOOK_RESEARCH_OUTCOME_BOARD"] = "HOOK_RESEARCH_OUTCOME_BOARD"
    workflow_route: WorkflowRoute = "workflow_a"
    status: BoardStatus
    season_id: str = Field(min_length=1)
    season_title: str = Field(min_length=1)
    monthly_storyline: str = Field(min_length=1)
    content_line: str = Field(min_length=1)
    episode_id: str | None = None
    scene_id: str | None = None
    created_at: datetime
    created_by: str = Field(min_length=1)
    human_owner: str = Field(min_length=1)
    output_language: str = "ru"


class ProducerHookSearchTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directive_id: str = Field(min_length=1)
    directive_type: Literal["HOOK_RESEARCH_FOR_WORKFLOW_A"]
    route: WorkflowRoute
    search_goal: str = Field(min_length=1)
    season_context: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    core_pain: str = Field(min_length=1)
    core_desire: str = Field(min_length=1)
    core_tension: str = Field(min_length=1)
    target_themes: list[str] = Field(default_factory=list, min_length=1)
    forbidden_themes: list[str] = Field(default_factory=list)
    desired_hook_mechanics: list[str] = Field(default_factory=list, min_length=1)
    platforms: list[str] = Field(default_factory=list, min_length=1)
    languages_regions: list[str] = Field(default_factory=list, min_length=1)
    creator_archetypes: list[str] = Field(default_factory=list, min_length=1)
    date_window: str = Field(min_length=1)
    performance_threshold: str = Field(min_length=1)
    source_count_target: int = Field(ge=1)
    hook_count_target: int = Field(ge=1)
    compliance_boundaries: list[str] = Field(default_factory=list, min_length=1)
    notes_for_research_agent: str | None = None

    @model_validator(mode="after")
    def validate_workflow_a_route(self) -> "ProducerHookSearchTask":
        if self.route != "workflow_a":
            raise ValueError("ProducerHookSearchTask.route must be workflow_a")
        if not self.search_goal.strip():
            raise ValueError("ProducerHookSearchTask.search_goal is required")
        return self


class ResearchScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    search_queries_used: list[str] = Field(default_factory=list, min_length=1)
    platform_filters: list[str] = Field(default_factory=list, min_length=1)
    region_filters: list[str] = Field(default_factory=list, min_length=1)
    language_filters: list[str] = Field(default_factory=list, min_length=1)
    date_filter: str = Field(min_length=1)
    creator_archetype_filter: list[str] = Field(default_factory=list)
    performance_filter: str = Field(min_length=1)
    topic_inclusion_filter: list[str] = Field(default_factory=list)
    topic_exclusion_filter: list[str] = Field(default_factory=list)
    compliance_filter: list[str] = Field(default_factory=list, min_length=1)
    search_limitations: list[str] = Field(default_factory=list)


class SearchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources_scanned: int = Field(ge=0)
    raw_candidates_collected: int = Field(ge=0)
    duplicates_removed: int = Field(ge=0)
    candidates_rejected: int = Field(ge=0)
    filtered_hook_opportunities: int = Field(ge=0)
    producer_original_hooks_added: int = Field(ge=0)
    research_mined_hooks_added: int = Field(ge=0)
    top_priority_hooks: int = Field(ge=0)
    risky_or_blocked_candidates: int = Field(ge=0)
    average_evidence_confidence: float = Field(ge=0, le=1)
    average_producer_alignment: float = Field(ge=0, le=1)
    rejection_reasons: dict[str, int] = Field(default_factory=dict)


class SourceEvidenceLogItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_item_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    source_platform: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_url_or_internal_ref: str = Field(min_length=1)
    creator_name_or_label: str | None = None
    creator_archetype: str = Field(min_length=1)
    date_detected: datetime
    content_date: datetime | None = None
    language: str = Field(min_length=1)
    region: str | None = None
    raw_hook_observed: str | None = None
    performance_signal_type: str = Field(min_length=1)
    performance_signal_notes: str = Field(min_length=1)
    evidence_strength: float = Field(ge=0, le=1)
    relevance_score: float = Field(ge=0, le=1)
    copy_risk: RiskLevel
    claim_risk: RiskLevel
    reuse_boundary: str = Field(min_length=1)


class HookOpportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority_rank: int = Field(ge=1)
    hook_id: str = Field(min_length=1)
    board_id: str = Field(min_length=1)
    directive_id: str = Field(min_length=1)
    opportunity_id: str | None = None
    workflow_route: WorkflowRoute = "workflow_a"
    input_mode: InputMode
    decision_status: DecisionStatus
    created_at: datetime
    updated_at: datetime

    season_id: str = Field(min_length=1)
    monthly_storyline: str = Field(min_length=1)
    content_line: str = Field(min_length=1)
    episode_id: str | None = None
    scene_id: str | None = None
    scene_type: str | None = None
    plot_function: str | None = None
    sales_intensity: Literal["none", "low", "medium", "high"]
    producer_topic: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    core_pain: str = Field(min_length=1)
    core_desire: str = Field(min_length=1)
    core_tension: str = Field(min_length=1)
    desired_cta_direction: str | None = None

    source_item_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    source_platform: str | None = None
    source_type: str | None = None
    creator_archetype: str | None = None
    source_recency_days: int | None = Field(default=None, ge=0)
    performance_signal: str | None = None
    performance_signal_strength: float | None = Field(default=None, ge=0, le=1)
    relative_baseline_note: str | None = None
    source_relevance_score: float | None = Field(default=None, ge=0, le=1)
    source_confidence_score: float | None = Field(default=None, ge=0, le=1)
    reuse_boundary: str = Field(min_length=1)
    producer_original_basis: list[str] = Field(default_factory=list)

    hook_mechanic: str = Field(min_length=1)
    attention_trigger: str = Field(min_length=1)
    opening_move: str = Field(min_length=1)
    visual_hook_type: str = Field(min_length=1)
    spoken_hook_type: str = Field(min_length=1)
    narrative_formula: str = Field(min_length=1)
    emotional_trigger: str = Field(min_length=1)
    retention_mechanic: str = Field(min_length=1)
    cta_pattern: str | None = None
    why_it_performed: str = Field(min_length=1)

    adapted_hook_for_jane: str = Field(min_length=1)
    first_frame_text: str = Field(min_length=1)
    spoken_opening: str = Field(min_length=1)
    video_angle: str = Field(min_length=1)
    micro_script_seed: str | None = None
    cta_direction: str = Field(min_length=1)
    visual_opening_direction: str = Field(min_length=1)
    tone_direction: str = Field(min_length=1)
    variant_a: str | None = None
    variant_b: str | None = None
    variant_c: str | None = None

    producer_alignment_score: float = Field(ge=0, le=1)
    audience_pain_match_score: float = Field(ge=0, le=1)
    hook_strength_score: float = Field(ge=0, le=1)
    evidence_confidence_score: float = Field(ge=0, le=1)
    trend_recency_score: float = Field(ge=0, le=1)
    originality_score: float = Field(ge=0, le=1)
    execution_ease_score: float = Field(ge=0, le=1)
    cta_fit_score: float = Field(ge=0, le=1)
    factual_safety_score: float = Field(ge=0, le=1)
    risk_penalty: float = Field(ge=0, le=1)
    final_priority_score: float = Field(ge=0, le=1)

    risk_level: RiskLevel
    claim_risk: RiskLevel
    copy_risk: RiskLevel
    tone_risk: RiskLevel
    brand_risk: RiskLevel
    platform_policy_risk: RiskLevel | None = None
    risk_notes: str = Field(min_length=1)
    required_rewrite: bool
    qa_status: QAStatus

    human_decision: HumanDecision | None = None
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None
    reviewer_notes: str | None = None
    next_action: str | None = None
    workflow_a_brief_id: str | None = None

    @model_validator(mode="after")
    def validate_mode_and_approval_rules(self) -> "HookOpportunity":
        if self.input_mode == "RESEARCH_MINED":
            if not self.source_item_refs:
                raise ValueError("RESEARCH_MINED hooks require source_item_refs")
            if not self.evidence_refs:
                raise ValueError("RESEARCH_MINED hooks require evidence_refs")
            if not self.performance_signal:
                raise ValueError("RESEARCH_MINED hooks require performance_signal")
        if self.input_mode == "PRODUCER_ORIGINAL":
            if self.source_item_refs or self.evidence_refs:
                raise ValueError("PRODUCER_ORIGINAL hooks must not contain source/evidence refs")
            if not self.producer_original_basis:
                raise ValueError("PRODUCER_ORIGINAL hooks require producer_original_basis")
        if self.human_decision == "APPROVE_FOR_WORKFLOW_A":
            if self.qa_status != "PASS":
                raise ValueError("Only QA PASS rows can be approved for Workflow A")
            if self.copy_risk in {"high", "blocker"}:
                raise ValueError("Blocker/high copy-risk hooks cannot be approved for Workflow A")
            if not is_acceptable_workflow_a_risk(self):
                raise ValueError("Only approved hooks with acceptable risk can enter Workflow A")
        return self


class ExpandedHookCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook_id: str = Field(min_length=1)
    priority_rank: int = Field(ge=1)
    input_mode: InputMode
    producer_context_summary: str = Field(min_length=1)
    source_signal_summary: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    audience_pain: str = Field(min_length=1)
    audience_desire: str = Field(min_length=1)
    core_tension: str = Field(min_length=1)
    extracted_pattern: str = Field(min_length=1)
    why_it_worked: str = Field(min_length=1)
    adaptation_boundary: str = Field(min_length=1)
    jane_adapted_hook: str = Field(min_length=1)
    first_frame_text: str = Field(min_length=1)
    spoken_opening: str = Field(min_length=1)
    visual_opening: str = Field(min_length=1)
    short_video_seed: str = Field(min_length=1)
    cta_direction: str = Field(min_length=1)
    risk_note: str = Field(min_length=1)
    rewrite_instruction: str | None = None
    recommended_decision: HumanDecision


class ApprovedWorkflowAHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved_hook_id: str = Field(min_length=1)
    approved_opportunity_id: str = Field(min_length=1)
    directive_id: str = Field(min_length=1)
    season_id: str = Field(min_length=1)
    episode_id: str | None = None
    scene_id: str | None = None
    selected_hook: str = Field(min_length=1)
    first_frame_text: str = Field(min_length=1)
    video_angle: str = Field(min_length=1)
    producer_context: dict[str, Any]
    source_context: dict[str, Any]
    evidence_refs: list[str] = Field(default_factory=list)
    factual_boundaries: list[str] = Field(default_factory=list, min_length=1)
    reuse_boundary: str = Field(min_length=1)
    cta_direction: str = Field(min_length=1)
    workflow_a_brief_status: Literal["READY_TO_BUILD", "BUILT"]


class QAReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qa_status: QAStatus
    producer_task_present: bool
    search_scope_matches_task: bool
    research_agent_only_collection: bool
    source_evidence_present: bool
    no_raw_source_dump_as_final: bool
    no_copying: bool
    factual_boundaries_respected: bool
    storyline_alignment: bool
    workflow_boundary_ok: bool
    decision_rules_enforced: bool
    qa_notes: list[str] = Field(default_factory=list)


class HookResearchOutcomeBoard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    board_header: BoardHeader
    producer_hook_search_task: ProducerHookSearchTask
    research_scope: ResearchScope
    search_summary: SearchSummary
    source_evidence_log: list[SourceEvidenceLogItem] = Field(default_factory=list)
    hook_opportunities: list[HookOpportunity] = Field(default_factory=list)
    expanded_hook_cards: list[ExpandedHookCard] = Field(default_factory=list)
    scoring_rubric: dict[str, float] = Field(default_factory=dict)
    approved_for_workflow_a: list[ApprovedWorkflowAHandoff] = Field(default_factory=list)
    rejected_or_held: list[dict[str, Any]] = Field(default_factory=list)
    qa_report: QAReport
    codex_runtime_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_board_boundaries(self) -> "HookResearchOutcomeBoard":
        if self.board_header.workflow_route != "workflow_a":
            raise ValueError("HookResearchOutcomeBoard can only route to workflow_a")
        if self.producer_hook_search_task.route != "workflow_a":
            raise ValueError("ProducerHookSearchTask route must be workflow_a")
        hook_directive_ids = {hook.directive_id for hook in self.hook_opportunities}
        if hook_directive_ids and self.producer_hook_search_task.directive_id not in hook_directive_ids:
            raise ValueError("hook opportunities must reference ProducerHookSearchTask directive_id")
        if not self.qa_report.workflow_boundary_ok:
            raise ValueError("HookResearchOutcomeBoard must preserve Workflow A boundaries")
        return self


def is_acceptable_workflow_a_risk(hook: HookOpportunity) -> bool:
    risk_values = [
        hook.risk_level,
        hook.claim_risk,
        hook.copy_risk,
        hook.tone_risk,
        hook.brand_risk,
        hook.platform_policy_risk or "none",
    ]
    return all(risk not in {"high", "blocker"} for risk in risk_values)


def is_workflow_a_eligible_hook(hook: HookOpportunity) -> bool:
    return (
        hook.human_decision == "APPROVE_FOR_WORKFLOW_A"
        and hook.qa_status == "PASS"
        and is_acceptable_workflow_a_risk(hook)
    )


__all__ = [
    "ApprovedWorkflowAHandoff",
    "BlockedReason",
    "BoardHeader",
    "BoardStatus",
    "DecisionStatus",
    "ExpandedHookCard",
    "HookOpportunity",
    "HookResearchBlockedResult",
    "HookResearchOutcomeBoard",
    "HumanDecision",
    "InputMode",
    "ProducerHookSearchTask",
    "QAReport",
    "QAStatus",
    "ResearchScope",
    "RiskLevel",
    "SearchSummary",
    "SourceEvidenceLogItem",
    "WorkflowRoute",
    "is_acceptable_workflow_a_risk",
    "is_workflow_a_eligible_hook",
]
