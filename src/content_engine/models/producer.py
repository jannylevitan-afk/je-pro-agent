from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Priority = Literal["low", "medium", "high", "urgent"]
ProducerDecisionValue = Literal["approve", "reject", "hold"]
SelectedWorkflow = Literal["workflow_a", "workflow_b"]
SalesFunction = Literal[
    "awareness",
    "problem_recognition",
    "belief_shift",
    "trust_building",
    "desire_creation",
    "objection_handling",
    "offer_reveal",
    "conversion",
    "retention",
    "upsell",
]
SceneType = Literal[
    "context",
    "personal_story",
    "problem_reveal",
    "behind_the_scenes",
    "experiment",
    "mistake",
    "lesson",
    "client_case",
    "social_proof",
    "myth_busting",
    "objection_handling",
    "product_creation",
    "offer_intro",
    "direct_offer",
    "faq",
    "decision_point",
    "community_interaction",
    "recap",
    "cliffhanger",
]
PlotFunction = Literal[
    "introduce_context",
    "raise_stakes",
    "show_conflict",
    "build_trust",
    "teach",
    "show_process",
    "show_proof",
    "shift_belief",
    "answer_objection",
    "create_desire",
    "invite_action",
    "close_loop",
    "open_next_loop",
]
WorkflowTaskTarget = Literal[
    "research_agent",
    "analyst",
    "brief_builder",
    "workflow_a",
    "workflow_b",
    "editorial_gate",
    "admin_hub",
]


class SeasonSeed(BaseModel):
    """Human strategy input that starts a new Producer planning cycle."""

    model_config = ConfigDict(extra="forbid")

    seed_id: str = Field(min_length=1)
    season_goal: str = Field(min_length=1)
    current_context: str = Field(min_length=1)
    offer_focus: str = Field(min_length=1)
    rubrics_to_emphasize: list[str] = Field(default_factory=list)
    audience_focus: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    date_range: str = Field(min_length=1)
    success_metrics: list[str] = Field(default_factory=list)


class CreatorProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    role: str
    niche: str
    positioning: str
    values: list[str] = Field(default_factory=list)
    tone: str
    personal_boundaries: list[str] = Field(default_factory=list)
    allowed_personal_themes: list[str] = Field(default_factory=list)
    forbidden_themes: list[str] = Field(default_factory=list)
    current_life_context: str | None = None


class ProductOffer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    offer_id: str
    name: str
    offer_type: str
    target_audience: str
    core_problem: str
    promised_transformation: str
    proof_assets: list[str] = Field(default_factory=list)
    main_objections: list[str] = Field(default_factory=list)
    funnel_steps: list[str] = Field(default_factory=list)
    cta_options: list[str] = Field(default_factory=list)
    availability: str = "evergreen"


class SeriesMemory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    open_loops: list[str] = Field(default_factory=list)
    answered_questions: list[str] = Field(default_factory=list)
    repeated_objections: list[str] = Field(default_factory=list)
    audience_signals: list[str] = Field(default_factory=list)
    published_scenes: list[str] = Field(default_factory=list)
    promises_made: list[str] = Field(default_factory=list)
    proof_used: list[str] = Field(default_factory=list)
    topics_to_avoid_repeating: list[str] = Field(default_factory=list)


class MetricsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reach: int | None = None
    impressions: int | None = None
    story_completion_rate: float | None = None
    watch_time: float | None = None
    saves: int | None = None
    shares: int | None = None
    comments: int | None = None
    dm_count: int | None = None
    link_clicks: int | None = None
    leads: int | None = None
    purchases: int | None = None
    revenue: float | None = None
    conversion_rate: float | None = None
    top_questions: list[str] = Field(default_factory=list)
    top_objections: list[str] = Field(default_factory=list)


class ProducerContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    creator: CreatorProfile
    brand: dict[str, Any] = Field(default_factory=dict)
    audience: list[str] = Field(default_factory=list)
    offers: list[ProductOffer] = Field(default_factory=list)
    current_workflow_state: str = "season_seeded"
    channels: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    season_seed: SeasonSeed
    metrics: MetricsSnapshot | None = None
    memory: SeriesMemory | None = None


class ProducerBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brief_id: str
    creator_name: str
    audience_summary: str
    product_summary: str
    season_goal: str
    constraints: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)


class EpisodePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    episode_id: str = Field(min_length=1)
    season_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    day_range: str = Field(min_length=1)
    episode_question: str = Field(min_length=1)
    conflict: str = Field(min_length=1)
    insight: str = Field(min_length=1)
    sales_function: SalesFunction
    scene_ids: list[str] = Field(default_factory=list)
    hook_to_next_episode: str = Field(min_length=1)


class SeasonBible(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    duration_days: int = Field(ge=1)
    season_thesis: str = Field(min_length=1)
    narrative_question: str = Field(min_length=1)
    main_conflict: str = Field(min_length=1)
    audience_goal: str = Field(min_length=1)
    product_role: str = Field(min_length=1)
    emotional_arc: list[str] = Field(default_factory=list)
    sales_arc: list[str] = Field(default_factory=list)
    episodes: list[EpisodePlan] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_minimum_episode_count(self) -> "SeasonBible":
        if len(self.episodes) < 3:
            raise ValueError("SeasonBible requires at least 3 episodes")
        return self


class SceneCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str = Field(min_length=1)
    episode_id: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    format: str = Field(min_length=1)
    scene_type: SceneType
    plot_function: PlotFunction
    sales_intensity: int = Field(ge=0, le=3)
    hook: str = Field(min_length=1)
    context: str = Field(min_length=1)
    conflict_or_question: str = Field(min_length=1)
    value_point: str = Field(min_length=1)
    proof_point: str | None = None
    offer_bridge: str | None = None
    cta: str | None = None
    next_hook: str | None = None
    required_assets: list[str] = Field(default_factory=list)
    qa_status: Literal["draft", "passed", "failed"] = "draft"

    @model_validator(mode="after")
    def validate_scene_story_and_business_function(self) -> "SceneCard":
        if not self.cta and not self.next_hook:
            raise ValueError("SceneCard requires CTA or next hook")
        if self.sales_intensity == 3 and not (self.proof_point and self.offer_bridge and self.cta):
            raise ValueError("direct offer scenes require proof_point, offer_bridge, and cta")
        return self


class ResearchDirective(BaseModel):
    """Producer task for Research Agent. Producer never collects data itself."""

    model_config = ConfigDict(extra="forbid")

    directive_id: str = Field(min_length=1)
    target_agent: Literal["research_agent"] = "research_agent"
    season_id: str = Field(min_length=1)
    episode_id: str = Field(min_length=1)
    scene_id: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    audience_segment: str = Field(min_length=1)
    content_theme: str = Field(min_length=1)
    platform_targets: list[str] = Field(default_factory=list)
    approved_source_groups: list[str] = Field(default_factory=list)
    search_goal: str = Field(min_length=1)
    must_collect: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    priority: Priority
    created_at: str = Field(min_length=1)


class ProducerDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str = Field(min_length=1)
    opportunity_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    decision: ProducerDecisionValue
    selected_workflow: SelectedWorkflow | None = None
    selected_platform: str | None = None
    priority: Priority
    production_intent: str = Field(min_length=1)
    season_id: str | None = None
    episode_id: str | None = None
    scene_id: str | None = None
    reason: str = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    human_notes: str | None = None
    created_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_approval_has_route(self) -> "ProducerDecision":
        if self.decision == "approve" and not self.selected_workflow:
            raise ValueError("approved ProducerDecision requires selected_workflow")
        if self.decision == "approve" and not self.selected_platform:
            raise ValueError("approved ProducerDecision requires selected_platform")
        return self


class ApprovedOpportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    opportunity_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    selected_workflow: SelectedWorkflow
    selected_platform: str = Field(min_length=1)
    priority: Priority
    production_intent: str = Field(min_length=1)
    core_idea: str = Field(min_length=1)
    jane_adaptation_brief: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    risk_flags: list[str] = Field(default_factory=list)
    season_id: str | None = None
    episode_id: str | None = None
    scene_id: str | None = None
    created_at: str = Field(min_length=1)


class WorkflowTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    target_agent: WorkflowTaskTarget
    priority: Priority
    payload: dict[str, Any] = Field(default_factory=dict)
    due_at: str | None = None


class ProducerQAReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    narrative_clarity: int = Field(ge=0, le=10)
    audience_relevance: int = Field(ge=0, le=10)
    sales_integration: int = Field(ge=0, le=10)
    content_variety: int = Field(ge=0, le=10)
    proof_strength: int = Field(ge=0, le=10)
    cta_clarity: int = Field(ge=0, le=10)
    operational_readiness: int = Field(ge=0, le=10)
    ethical_safety: int = Field(ge=0, le=10)
    issues: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)
    created_at: str = Field(min_length=1)

    @property
    def total_score(self) -> float:
        raw_total = (
            self.narrative_clarity
            + self.audience_relevance
            + self.sales_integration
            + self.content_variety
            + self.proof_strength
            + self.cta_clarity
            + self.operational_readiness
            + self.ethical_safety
        )
        return round((raw_total / 80) * 100, 2)

    @model_validator(mode="after")
    def validate_pass_thresholds(self) -> "ProducerQAReport":
        if self.ethical_safety < 9:
            raise ValueError("ethical_safety must be at least 9")
        if self.narrative_clarity < 8:
            raise ValueError("narrative_clarity must be at least 8")
        if self.sales_integration < 8:
            raise ValueError("sales_integration must be at least 8")
        if self.cta_clarity < 7:
            raise ValueError("cta_clarity must be at least 7")
        if self.total_score < 80:
            raise ValueError("ProducerQAReport total score must be at least 80/100")
        return self


class ProducerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brief: ProducerBrief
    season: SeasonBible
    episodes: list[EpisodePlan] = Field(default_factory=list)
    scenes: list[SceneCard] = Field(default_factory=list)
    research_directives: list[ResearchDirective] = Field(default_factory=list)
    decisions: list[ProducerDecision] = Field(default_factory=list)
    approved_opportunities: list[ApprovedOpportunity] = Field(default_factory=list)
    workflow_tasks: list[WorkflowTask] = Field(default_factory=list)
    qa_report: ProducerQAReport
    memory: SeriesMemory | None = None


__all__ = [
    "ApprovedOpportunity",
    "CreatorProfile",
    "EpisodePlan",
    "MetricsSnapshot",
    "PlotFunction",
    "Priority",
    "ProducerBrief",
    "ProducerContext",
    "ProducerDecision",
    "ProducerDecisionValue",
    "ProducerOutput",
    "ProducerQAReport",
    "ProductOffer",
    "ResearchDirective",
    "SalesFunction",
    "SceneCard",
    "SceneType",
    "SeasonBible",
    "SeasonSeed",
    "SelectedWorkflow",
    "SeriesMemory",
    "WorkflowTask",
    "WorkflowTaskTarget",
]
