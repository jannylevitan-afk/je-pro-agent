from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


EditorialApprovalStatus = Literal["approved_for_human_review", "needs_revision", "rejected"]


class EditorialReviewResult(BaseModel):
    """Editor / QA Gate result before an asset reaches human review."""

    model_config = ConfigDict(extra="forbid")

    review_id: str = Field(min_length=1)
    content_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    passed: bool
    approval_status: EditorialApprovalStatus
    score: float = Field(ge=0.0, le=1.0)
    failed_checks: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)
    factual_risk_flags: list[str] = Field(default_factory=list)
    voice_risk_flags: list[str] = Field(default_factory=list)
    review_pass_number: int = Field(ge=1, le=3)
    created_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_passed_status(self) -> "EditorialReviewResult":
        if self.passed and self.approval_status != "approved_for_human_review":
            raise ValueError("passed editorial reviews must be approved_for_human_review")
        if not self.passed and self.approval_status == "approved_for_human_review":
            raise ValueError("failed editorial reviews cannot be approved_for_human_review")
        return self


__all__ = ["EditorialApprovalStatus", "EditorialReviewResult"]
