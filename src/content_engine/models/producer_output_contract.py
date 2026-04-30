from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from content_engine.models.producer import (
    EpisodePlan,
    Priority,
    ProducerBrief,
    ProducerQAReport,
    SceneCard,
    SeasonBible,
)


ProducerDisplayTaskTarget = Literal[
    "copywriter_agent",
    "designer_agent",
    "video_asset_agent",
    "sales_automation_agent",
    "manual_publishing_calendar",
    "analytics_agent",
]
ProducerDisplayWorkflow = Literal["workflow_a", "workflow_b", "cross_workflow", "manual_ops"]


class ProducerOutputSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    items: list[str] = Field(default_factory=list)


class ProducerDisplayTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    target_agent: ProducerDisplayTaskTarget
    priority: Priority
    workflow: ProducerDisplayWorkflow
    responsibilities: list[str] = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_workflow_boundaries(self) -> "ProducerDisplayTask":
        if self.target_agent == "video_asset_agent" and self.workflow != "workflow_a":
            raise ValueError("Video / AssetAgent must receive Workflow A tasks")
        if self.target_agent == "copywriter_agent" and self.workflow != "workflow_b":
            raise ValueError("CopywriterAgent must receive Workflow B tasks")
        if self.target_agent == "manual_publishing_calendar" and "no auto-publishing" not in self.constraints:
            raise ValueError("Manual Publishing / Calendar must preserve no auto-publishing")
        return self


class ReadableProducerOutput(BaseModel):
    """Human-readable Producer handoff for season review and admin display."""

    model_config = ConfigDict(extra="forbid")

    output_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    subtitle: str = Field(min_length=1)
    section_order: list[str] = Field(min_length=1)
    producer_brief: ProducerBrief
    audience_segments: list[ProducerOutputSection] = Field(default_factory=list)
    product_map: list[ProducerOutputSection] = Field(default_factory=list)
    product_to_story_mapping: list[ProducerOutputSection] = Field(default_factory=list)
    season_bible: SeasonBible
    content_lines: list[ProducerOutputSection] = Field(default_factory=list)
    emotional_arc: list[ProducerOutputSection] = Field(default_factory=list)
    sales_arc: list[ProducerOutputSection] = Field(default_factory=list)
    episodes: list[EpisodePlan] = Field(default_factory=list)
    scene_cards: list[SceneCard] = Field(default_factory=list)
    cta_library: list[ProducerOutputSection] = Field(default_factory=list)
    lead_magnets: list[ProducerOutputSection] = Field(default_factory=list)
    proof_plan: list[ProducerOutputSection] = Field(default_factory=list)
    objection_handling: list[ProducerOutputSection] = Field(default_factory=list)
    content_rhythm: list[ProducerOutputSection] = Field(default_factory=list)
    visual_system: list[ProducerOutputSection] = Field(default_factory=list)
    sales_automation_setup: list[ProducerOutputSection] = Field(default_factory=list)
    metrics_plan: list[ProducerOutputSection] = Field(default_factory=list)
    series_memory: list[ProducerOutputSection] = Field(default_factory=list)
    agent_tasks: list[ProducerDisplayTask] = Field(default_factory=list)
    qa_report: ProducerQAReport
    guardrails: list[str] = Field(default_factory=list)
    final_assembly: list[ProducerOutputSection] = Field(default_factory=list)
    first_actions: list[str] = Field(default_factory=list)


__all__ = [
    "ProducerDisplayTask",
    "ProducerDisplayTaskTarget",
    "ProducerDisplayWorkflow",
    "ProducerOutputSection",
    "ReadableProducerOutput",
]
