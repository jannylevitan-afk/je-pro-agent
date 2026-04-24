import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AnalyticsPlatform = Literal["instagram", "linkedin", "telegram", "tiktok", "youtube"]
AttributionModel = Literal["first_touch", "last_touch", "time_decay"]
InquiryType = Literal["broker", "developer", "investor", "lifestyle", "ailla", "none"]
PerformanceTier = Literal["top", "average", "weak"]
SignalScope = Literal["hook_type", "content_theme", "platform_lane"]
SignalType = Literal["boost", "monitor", "suppress"]


class ContentPerformanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    linked_content_item_id: str
    platform: AnalyticsPlatform
    platform_lane: str | None = None
    content_theme: str | None = None
    hook_type: str | None = None
    reach: int = Field(ge=0)
    impressions: int = Field(ge=0)
    saves: int = Field(ge=0)
    shares: int = Field(ge=0)
    comments: int = Field(ge=0)
    profile_visits: int = Field(ge=0)
    dms_received: int = Field(ge=0)
    likes: int = Field(ge=0)
    link_clicks: int = Field(ge=0)
    inquiry_type: InquiryType = "none"
    attribution_model: AttributionModel
    deal_influenced: bool = False
    performance_tier: PerformanceTier | None = None


class DecisionMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engagement_rate: float = Field(ge=0.0)
    save_rate: float = Field(ge=0.0)
    share_rate: float = Field(ge=0.0)
    dm_rate: float = Field(ge=0.0)
    ctr: float = Field(ge=0.0)


class FeedbackSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_id: str
    signal_scope: SignalScope
    dimension_value: str
    signal_type: SignalType
    performance_tier: PerformanceTier
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class TrackingEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_name: str
    entity_id: str
    occurred_at: str

    @model_validator(mode="after")
    def validate_event_name(self) -> "TrackingEvent":
        if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", self.event_name):
            raise ValueError("Tracking events must use lowercase_with_underscores")
        return self
