from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


VideoPlatform = Literal["instagram", "tiktok", "youtube", "linkedin"]
HookType = Literal[
    "story_moment",
    "tactical_tip",
    "data_stat_callout",
    "bts_fragment",
    "market_warning",
]
VideoScriptStatus = Literal["scripted", "filmed", "published"]
VideoPublishStatus = Literal["ready", "published"]


class VideoHook(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook_id: str
    source_item_id: str
    platform: VideoPlatform
    content_theme: str
    angle: str
    hook_text: str
    hook_type: HookType
    score: int = Field(ge=1, le=10)


class VideoScript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    script_id: str
    source_item_id: str
    title: str
    platform: VideoPlatform
    hook_text: str
    script_text: str
    cta: str
    filming_priority: int = Field(ge=1)
    status: VideoScriptStatus


class FilmingCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    linked_script_id: str
    filming_priority: int = Field(ge=1)
    shoot_date: str | None = None
    filmed: bool = False
    raw_file_link: str | None = None


class VideoPublishItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    publish_item_id: str
    linked_script_id: str
    platform: VideoPlatform
    caption: str
    publish_date: str | None = None
    status: VideoPublishStatus

    @model_validator(mode="after")
    def validate_publish_state(self) -> "VideoPublishItem":
        if self.status == "published" and not self.publish_date:
            raise ValueError("published items require publish_date")
        return self
