from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


BriefWorkflow = Literal["workflow_a", "workflow_b"]


class BriefBase(BaseModel):
    """Shared evidence-bounded brief shape created after Producer approval."""

    model_config = ConfigDict(extra="forbid")

    brief_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    opportunity_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    workflow: BriefWorkflow
    selected_platform: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    audience_segment: str = Field(min_length=1)
    production_intent: str = Field(min_length=1)
    core_idea: str = Field(min_length=1)
    angle: str = Field(min_length=1)
    emotional_trigger: str = Field(min_length=1)
    source_summary: str = Field(min_length=1)
    source_text_excerpt: str = Field(min_length=1)
    what_performed: str = Field(min_length=1)
    jane_adaptation_instruction: str = Field(min_length=1)
    factual_boundaries: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    must_not_include: list[str] = Field(default_factory=list)
    tone_rules: list[str] = Field(default_factory=list)
    opening_direction: str = Field(min_length=1)
    quality_criteria: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    season_id: str | None = None
    episode_id: str | None = None
    scene_id: str | None = None


class WorkflowBBrief(BriefBase):
    workflow: Literal["workflow_b"]
    publish_language: Literal["ru", "en"] = "ru"
    internal_working_language: Literal["ru"] = "ru"
    platform_variants: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_single_platform_lane(self) -> "WorkflowBBrief":
        if self.platform_variants:
            raise ValueError("Workflow B briefs cannot include platform variants")
        if self.selected_platform == "linkedin" and self.publish_language != "en":
            raise ValueError("LinkedIn Workflow B briefs must publish in English")
        return self


class WorkflowABrief(BriefBase):
    workflow: Literal["workflow_a"]
    video_refs: list[str] = Field(default_factory=list)
    source_hook: str | None = None
    transcript_source: str | None = None


class BriefBuilderResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved_id: str = Field(min_length=1)
    brief: WorkflowABrief | WorkflowBBrief
    created_at: str = Field(min_length=1)


__all__ = ["BriefBase", "BriefBuilderResult", "BriefWorkflow", "WorkflowABrief", "WorkflowBBrief"]
