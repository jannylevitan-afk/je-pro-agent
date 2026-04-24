from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


PipelineLayer = Literal["research_agent", "workflow_a", "workflow_b"]

PipelineEventName = Literal[
    # Research Agent
    "data_collected",
    "routed_to_workflow_a",
    "routed_to_workflow_b",
    # Workflow A stages
    "hooks_developed",
    "script_generated",
    "filmed",
    "published",
    "measured",
    # Workflow B stages
    "data_received",
    "source_normalized",
    "insight_created",
    "idea_created",
    "brief_created",
    "draft_generated",
    "ai_edited",
    "human_reviewed",
    "approved",
    "push_to_notion",
    "scheduled",
    # Fail states
    "rejected_at_idea",
    "rejected_at_draft",
    "blocked_factual_safety",
    "failed_quality_gate",
]

_FAILURE_EVENT_NAMES: frozenset[str] = frozenset({
    "rejected_at_idea",
    "rejected_at_draft",
    "blocked_factual_safety",
    "failed_quality_gate",
})


class PipelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_name: PipelineEventName
    pipeline: PipelineLayer
    entity_id: str
    occurred_at: str
    is_failure: bool = False
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_failure_consistency(self) -> "PipelineEvent":
        is_fail = self.event_name in _FAILURE_EVENT_NAMES
        if is_fail and not self.is_failure:
            raise ValueError(f"'{self.event_name}' is a fail state — set is_failure=True")
        if self.is_failure and not is_fail:
            raise ValueError("is_failure=True requires a failure event_name")
        if self.is_failure and not self.failure_reason:
            raise ValueError("failure events require failure_reason")
        return self
