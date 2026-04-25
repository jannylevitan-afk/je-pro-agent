from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PreflightStatus = Literal["ready", "needs_context", "blocked"]
PreflightAction = Literal["continue", "ask_user", "stop"]
IdeaVerdict = Literal["keep", "kill", "refine"]
InsightVerdict = Literal["strong", "needs_refinement", "weak"]
RiskLevel = Literal["low", "medium", "high"]
AuthorProfile = Literal["generic", "jane_levitan", "custom"]
HookGateVerdict = Literal["keep", "rewrite", "kill"]


class AvailableContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_dossier: bool = False
    voice_profile: bool = False
    source_material: bool = False


class WriterTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_topic: str
    source_material: str
    target_audience: str
    platform: str
    goal: str
    tone_of_voice: str
    length: str
    cta_type: str
    author_profile: AuthorProfile = "jane_levitan"
    available_context: AvailableContext = Field(default_factory=AvailableContext)

    @model_validator(mode="after")
    def normalize_core_strings(self) -> "WriterTaskInput":
        self.raw_topic = self.raw_topic.strip()
        self.source_material = self.source_material.strip()
        self.target_audience = self.target_audience.strip()
        self.platform = self.platform.strip().lower()
        self.goal = self.goal.strip().lower()
        self.tone_of_voice = self.tone_of_voice.strip().lower()
        self.length = self.length.strip().lower()
        self.cta_type = self.cta_type.strip()
        return self


class AuthorVoiceObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author_name: str
    public_facts: list[str] = Field(default_factory=list)
    private_facts_do_not_use: list[str] = Field(default_factory=list)
    audience_segments: list[str] = Field(default_factory=list)
    voice_registers: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)
    forbidden_structures: list[str] = Field(default_factory=list)
    taboo_topics: list[str] = Field(default_factory=list)
    signature_phrases: list[str] = Field(default_factory=list)
    public_opinions: list[str] = Field(default_factory=list)
    platform_rules: dict[str, str] = Field(default_factory=dict)
    qa_rules: list[str] = Field(default_factory=list)


class WriterPreflight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: PreflightStatus
    missing_inputs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    next_action: PreflightAction


class TaskClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_type: str
    platform: str
    target_audience: str
    goal: str
    required_voice_mode: str
    risk_level: RiskLevel
    fact_verification_required: bool
    notes: list[str] = Field(default_factory=list)


class WriterInsightCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str
    angle: str
    emotional_trigger: str
    audience_fit: str
    hidden_tension: str
    promise: str
    risk: str
    assumptions: list[str] = Field(default_factory=list)


class InsightQualityScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clarity: int = Field(ge=0, le=10)
    emotional_strength: int = Field(ge=0, le=10)
    audience_fit: int = Field(ge=0, le=10)
    originality: int = Field(ge=0, le=10)


class InsightExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_card: WriterInsightCard
    quality_score: InsightQualityScore
    verdict: InsightVerdict


class VoiceSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author_profile: AuthorProfile
    primary_register: str
    secondary_register: str | None = None
    reason: str
    rhythm_rules: list[str] = Field(default_factory=list)
    opening_type: str
    ending_type: str
    phrases_allowed: list[str] = Field(default_factory=list)
    phrases_forbidden: list[str] = Field(default_factory=list)
    emoji_policy: str


class ContentIdea(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idea_id: str
    title: str
    core_message: str
    emotional_trigger: str
    audience_value: str
    format_suggestion: str
    platform_fit: list[str]
    register_fit: str
    strength_score: int = Field(ge=1, le=10)
    verdict: IdeaVerdict


class KilledIdea(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idea: str
    reason: str


class IdeaGenerationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ideas: list[ContentIdea]
    killed_ideas: list[KilledIdea] = Field(default_factory=list)
    best_idea: dict[str, str]


class IdeaGateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: list[str] = Field(default_factory=list)
    killed: list[str] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)
    selected_idea: str


class WriterContentBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience: str
    platform: str
    goal: str
    core_message: str
    hook_direction: str
    emotional_trigger: str
    structure: list[str]
    tone_of_voice: str
    voice_register: str
    length: str
    cta: str
    required_facts: list[str] = Field(default_factory=list)
    forbidden_facts: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    examples_or_references: list[str] = Field(default_factory=list)


class WriterDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: str
    voice_register: str
    title: str
    hook: str
    body: str
    cta: str
    notes: list[str] = Field(default_factory=list)


class EditorDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    main_issue: str
    hook_score: int = Field(ge=0, le=10)
    clarity_score: int = Field(ge=0, le=10)
    emotional_score: int = Field(ge=0, le=10)
    voice_preservation_score: int = Field(ge=0, le=10)
    fact_safety_score: int = Field(ge=0, le=10)


class EditedVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook: str
    body: str
    cta: str


class EditingLayerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    editor_diagnosis: EditorDiagnosis
    edited_version: EditedVersion
    changes_made: list[str] = Field(default_factory=list)
    removed_phrases: list[str] = Field(default_factory=list)
    final_score: int = Field(ge=0, le=10)


class QAReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    issues: list[str] = Field(default_factory=list)
    fixes_applied: list[str] = Field(default_factory=list)
    requires_human_review: bool
    final_risk_level: RiskLevel


class TextOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str
    text: str
    reason: str


class WriterEntityOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preflight: WriterPreflight
    task_classification: TaskClassification
    insight_card: WriterInsightCard
    quality_score: InsightQualityScore
    voice_selection: VoiceSelection
    ideas: list[ContentIdea]
    killed_ideas: list[KilledIdea] = Field(default_factory=list)
    selected_idea: ContentIdea
    idea_gate: IdeaGateResult
    content_brief: WriterContentBrief
    draft: WriterDraft
    editor_diagnosis: EditorDiagnosis
    edited_final: EditedVersion
    hook_options: list[TextOption] = Field(default_factory=list)
    cta_options: list[TextOption] = Field(default_factory=list)
    qa_report: QAReport


class VideoHookOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook_id: str
    hook_text: str
    hook_type: str
    emotional_trigger: str
    why_it_works: str
    best_platform: str
    voice_register: str
    risk: str
    improved_version: str


class VideoTopicOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_id: str
    title: str
    angle: str
    target_audience: str
    emotional_trigger: str
    why_people_would_watch: str
    best_platform: str
    suggested_format: str
    voice_register: str


class BestVideoChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook_id: str = ""
    topic_id: str = ""
    reason: str


class VideoHookQualityGate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook_id: str
    specific: bool
    curiosity_or_tension: bool
    audience_clear: bool
    real_payoff: bool
    deliverable: bool
    emotionally_sharp: bool
    voice_fit: bool
    verdict: HookGateVerdict


class VideoHooksTopicsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_hooks: list[VideoHookOption]
    topics: list[VideoTopicOption]
    best_hook: BestVideoChoice
    best_topic: BestVideoChoice
    hook_quality_gate: list[VideoHookQualityGate]
