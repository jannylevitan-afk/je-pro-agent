from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RunStatus = Literal["success", "partial", "failed", "stale"]


class MonitoringRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    connector: str
    source_name: str
    started_at: str
    finished_at: str
    fetched_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    last_success_at: str
    error_type: str
    retry_count: int = Field(ge=0, le=3)
    staleness_hours: int = Field(ge=0)
    run_status: RunStatus
