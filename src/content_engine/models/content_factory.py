from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ContentFactoryRunStatus = Literal["created", "running", "completed", "failed", "partial"]
HumanReviewStatus = Literal["approved_for_human_review", "needs_revision", "rejected", "archived"]
HumanReviewWorkflow = Literal["workflow_a", "workflow_b"]


class HumanReviewAsset(BaseModel):
    """Final Admin Hub object. It is review-ready, not scheduled or published."""

    model_config = ConfigDict(extra="forbid")

    content_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    opportunity_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    brief_id: str = Field(min_length=1)
    workflow: HumanReviewWorkflow
    platform: str = Field(min_length=1)
    title: str = Field(min_length=1)
    pillar: str = Field(min_length=1)
    audience_segment: str = Field(min_length=1)
    approval_status: HumanReviewStatus
    final_text: str | None = None
    internal_ru_master: str | None = None
    selected_hook: str | None = None
    script: str | None = None
    filming_card: str | None = None
    editor_score: float = Field(ge=0.0, le=1.0)
    revision_notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    season_id: str | None = None
    episode_id: str | None = None
    scene_id: str | None = None
    created_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_workflow_payload(self) -> "HumanReviewAsset":
        if self.workflow == "workflow_b" and not self.final_text:
            raise ValueError("Workflow B HumanReviewAsset requires final_text")
        if self.workflow == "workflow_a" and not (self.selected_hook and self.script and self.filming_card):
            raise ValueError("Workflow A HumanReviewAsset requires selected_hook, script, and filming_card")
        return self


class ContentFactoryRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    status: ContentFactoryRunStatus
    started_at: str = Field(min_length=1)
    completed_at: str | None = None
    research_handoff_count: int = Field(ge=0)
    opportunity_count: int = Field(ge=0)
    producer_decision_count: int = Field(ge=0)
    workflow_a_asset_count: int = Field(ge=0)
    workflow_b_asset_count: int = Field(ge=0)
    human_review_asset_count: int = Field(ge=0)
    output_files: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


__all__ = [
    "ContentFactoryRunResult",
    "ContentFactoryRunStatus",
    "HumanReviewAsset",
    "HumanReviewStatus",
    "HumanReviewWorkflow",
]
