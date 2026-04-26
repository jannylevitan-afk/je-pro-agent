from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Platform = Literal["instagram", "linkedin", "telegram"]
PlatformLane = Literal["instagram_lifestyle", "instagram_professional", "linkedin_b2b"]
Language = Literal["ru", "en"]
FunnelRole = Literal["attention", "affinity", "authority", "conversion"]
LengthTarget = Literal["short", "medium", "long"]
SourceRigor = Literal["standard", "expert", "market-critical"]


class DraftBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    platform: Platform
    platform_lane: PlatformLane
    working_language: Language
    publish_language: Language
    audience_portrait: str
    voice_register: str
    funnel_role: FunnelRole
    draft_text_ru: str
    draft_text_en: str | None = None

    @model_validator(mode="after")
    def validate_language_policy(self) -> "DraftBundle":
        if self.platform_lane == "linkedin_b2b":
            if self.working_language != "ru":
                raise ValueError("LinkedIn working language must stay Russian in Notion")
            if self.publish_language != "en":
                raise ValueError("LinkedIn publish language must be English")
            if not self.draft_text_en:
                raise ValueError("LinkedIn requires an English publish version")
        return self


class SourceNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str
    source_name: str
    source_url: str
    date_collected: str
    platform: Platform | str
    topic_guess: str
    audience_guess: str
    content_type_guess: str
    engagement_signals: dict[str, int]
    raw_text: str


class InsightCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience: str
    platform: Platform | str
    topic: str = ""
    angle: str = ""
    audience_fit: str = ""
    content_theme: str
    content_pillar: str
    narrative_type: str
    priority: int
    reuse_score: int
    emotional_trigger: str
    useful_lesson: str


class IdeaCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    working_title: str
    target_platform: Platform
    platform_lane: PlatformLane
    language_mode: Language
    funnel_role: FunnelRole
    target_audience: str
    content_pillar: str
    emotional_hook: str
    useful_point: str
    desired_reaction: str
    suggested_format: str


class ContentBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience: str
    platform: Platform
    platform_lane: PlatformLane
    working_language: Language
    publish_language: Language
    funnel_role: FunnelRole
    purpose: str
    angle: str
    hook: str
    key_points: list[str]
    cta_type: str
    tone: str
    length_target: LengthTarget
    engagement_objective: str
    fact_pack: list[str]
    source_rigor: SourceRigor
    reference_sources: list[str]
    analyst_tz: str = ""

    @model_validator(mode="after")
    def validate_linkedin_language_policy(self) -> "ContentBrief":
        if self.platform_lane == "linkedin_b2b":
            if self.working_language != "ru":
                raise ValueError("LinkedIn briefs must keep Russian working language")
            if self.publish_language != "en":
                raise ValueError("LinkedIn briefs must publish in English")
        if self.source_rigor in {"expert", "market-critical"}:
            if not 3 <= len(self.reference_sources) <= 5:
                raise ValueError("expert and market-critical briefs require 3 to 5 reference sources")
        return self


BriefWorkflowStage = Literal["brief_ready", "revision_needed", "draft_in_progress", "done"]
BriefReviewDecision = Literal["pending", "approved", "needs_rewrite", "re_brief", "deleted"]


class BriefRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brief_id: str
    title: str
    audience_portrait: str
    platform_lane: PlatformLane
    language_mode: Language
    funnel_role: FunnelRole
    workflow_stage: BriefWorkflowStage
    review_decision: BriefReviewDecision
    linked_draft_id: str | None = None
    revision_requested_at: str | None = None
    review_notes: str | None = None
    source_rigor: SourceRigor = "standard"
    reference_sources: list[str] = Field(default_factory=list)
