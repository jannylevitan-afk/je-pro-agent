from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SuggestedWorkflow = Literal["workflow_a", "workflow_b", "both", "drop"]
RiskLevel = Literal["low", "medium", "high"]


class OpportunityCandidate(BaseModel):
    """Analyst output that Producer reviews before any writing or video work starts."""

    model_config = ConfigDict(extra="forbid")

    opportunity_id: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    core_idea: str = Field(min_length=1)
    jane_adaptation_brief: str = Field(min_length=1)
    audience_segment: str = Field(min_length=1)
    content_theme: str = Field(min_length=1)
    rubric: str = Field(min_length=1)
    suggested_workflow: SuggestedWorkflow
    suggested_platform: str | None = None
    popularity_label: str = Field(min_length=1)
    public_metrics: dict[str, int] = Field(default_factory=dict)
    what_performed: str = Field(min_length=1)
    emotional_trigger: str = Field(min_length=1)
    strategic_fit_score: float = Field(ge=0.0, le=1.0)
    evidence_strength_score: float = Field(ge=0.0, le=1.0)
    novelty_score: float = Field(ge=0.0, le=1.0)
    audience_fit_score: float = Field(ge=0.0, le=1.0)
    production_complexity_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    risk_flags: list[str] = Field(default_factory=list)
    analyst_reason: str = Field(min_length=1)
    created_at: str = Field(min_length=1)

    @property
    def opportunity_score(self) -> float:
        """Weighted score used by Producer/Opportunity Queue for first-pass ranking."""

        production_feasibility = 1.0 - self.production_complexity_score
        risk_penalty = {"low": 0.0, "medium": 0.07, "high": 0.20}[self.risk_level]
        score = (
            0.30 * self.evidence_strength_score
            + 0.25 * self.strategic_fit_score
            + 0.20 * self.novelty_score
            + 0.15 * self.audience_fit_score
            + 0.10 * production_feasibility
            - risk_penalty
        )
        return round(max(0.0, min(1.0, score)), 4)


__all__ = ["OpportunityCandidate", "RiskLevel", "SuggestedWorkflow"]
