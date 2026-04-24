from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RoutingDecision = Literal["workflow_a", "workflow_b", "both", "drop"]
ProcessingState = Literal["collected", "normalized", "partial", "failed"]


class SourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    source_type: str
    source_name: str
    source_url: str
    external_item_id: str
    collected_at: str
    published_at: str
    content_hash: str
    dedupe_key: str
    audience_segment: str
    content_theme: str
    raw_payload: dict[str, Any]
    transcript_text: str
    media_urls: list[str]
    engagement_signals: dict[str, int]
    routing_decision: RoutingDecision
    routing_reason: str
    routing_confidence: float = Field(ge=0.0, le=1.0)
    processing_state: ProcessingState
