from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SearchPlatform = Literal["youtube", "tiktok", "instagram"]
SearchLanguage = Literal["ru", "en"]


class HookSearchAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_key: str = Field(min_length=1)
    platform: SearchPlatform
    language: SearchLanguage
    query: str = Field(min_length=1)
    query_intent: str = Field(min_length=1)


class HookTopicSearchBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_key: str = Field(min_length=1)
    order_index: int = Field(ge=1)
    qualified_target: int = Field(ge=1)
    platform_targets: dict[SearchPlatform, int]
    language_targets: dict[SearchLanguage, int]
    stop_condition: str = Field(min_length=1)
    search_attempts: list[HookSearchAttempt] = Field(default_factory=list, min_length=1)


class HookSearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directive_id: str = Field(min_length=1)
    source_count_target: int = Field(ge=1)
    platform_source_targets: dict[SearchPlatform, int]
    topic_source_targets: dict[str, int]
    language_source_targets: dict[SearchLanguage, int]
    topic_batches: list[HookTopicSearchBatch] = Field(default_factory=list, min_length=1)
    notes_for_research_agent: list[str] = Field(default_factory=list)


__all__ = [
    "HookSearchAttempt",
    "HookSearchPlan",
    "HookTopicSearchBatch",
    "SearchLanguage",
    "SearchPlatform",
]
