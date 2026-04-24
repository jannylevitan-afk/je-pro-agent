from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from content_engine.models.workflow_b import BriefRecord, DraftBundle, FunnelRole, Language, Platform, PlatformLane


LanguageMode = Literal["ru", "en"]
WorkflowStage = Literal[
    "draft_generated",
    "ai_edited",
    "awaiting_review",
    "moved_to_calendar",
    "revision_needed",
    "archived",
]
ReviewDecision = Literal["pending", "approved", "needs_rewrite", "re_brief", "deleted"]
FactualSafety = Literal["clean", "needs_human_confirmation", "blocked"]
ApprovalStatus = Literal["approved", "needs_revision"]
ReviewActionDecision = Literal["approved", "needs_rewrite", "re_brief", "deleted"]
EventName = Literal[
    "draft_submitted_for_review",
    "draft_reviewed",
    "rewrite_requested",
    "brief_revision_requested",
    "calendar_item_scheduled",
    "draft_archived",
]
EventEntityType = Literal["draft", "brief", "calendar_item"]
EventStatus = Literal["pending", "completed", "failed"]


class DraftRecord(DraftBundle):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    language_mode: LanguageMode
    version: int = Field(ge=1)
    workflow_stage: WorkflowStage
    review_decision: ReviewDecision
    review_notes: str | None = None
    ai_edited: bool = False
    seven_point_test_passed: bool = False
    factual_safety: FactualSafety
    linked_brief_id: str | None = None
    linked_calendar_id: str | None = None
    parent_draft_id: str | None = None
    review_requested_at: str | None = None
    approval_decided_at: str | None = None
    archived: bool = False


class ReviewAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReviewActionDecision
    decided_at: str
    notes: str | None = None
    rewritten_text_ru: str | None = None
    rewritten_text_en: str | None = None

    @model_validator(mode="after")
    def validate_notes_requirement(self) -> "ReviewAction":
        if self.decision == "needs_rewrite" and not self.notes:
            raise ValueError("needs_rewrite requires review notes")
        if self.decision == "needs_rewrite" and not self.rewritten_text_ru:
            raise ValueError("needs_rewrite requires rewritten_text_ru")
        return self


class CalendarItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calendar_item_id: str
    source_draft_id: str
    title: str
    platform: Platform
    platform_lane: PlatformLane
    language_mode: LanguageMode
    working_language: Language
    publish_language: Language
    audience_portrait: str
    voice_register_used: str
    funnel_role: FunnelRole
    hook: str | None = None
    pillar: str | None = None
    final_text_ru: str
    final_text_en: str | None = None
    publish_date_target: str | None = None
    approval_status: ApprovalStatus
    approval_decided_at: str

    @model_validator(mode="after")
    def validate_language_outputs(self) -> "CalendarItem":
        if self.platform_lane == "linkedin_b2b":
            if self.publish_language != "en":
                raise ValueError("LinkedIn publish language must stay English")
            if not self.final_text_en:
                raise ValueError("LinkedIn requires an English publish version")
        return self


class OrchestrationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_name: EventName
    entity_type: EventEntityType
    entity_id: str
    status: EventStatus
    triggered_at: str
    draft_id: str | None = None
    brief_id: str | None = None
    calendar_item_id: str | None = None
    payload_ref: str | None = None


class ApprovalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    updated_draft: DraftRecord
    next_draft: DraftRecord | None = None
    calendar_item: CalendarItem | None = None
    brief_update: BriefRecord | None = None
    events: list[OrchestrationEvent]
