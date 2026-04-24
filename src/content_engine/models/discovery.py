from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ApprovalState = Literal["pending", "approved", "rejected"]
Platform = Literal["instagram", "linkedin", "tiktok", "telegram"]


class DiscoveryCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    handle: str
    platform: Platform
    segment: str
    score: int = Field(ge=0, le=10)
    why_relevant: str
    approved: ApprovalState
    added_to_monitoring: bool
