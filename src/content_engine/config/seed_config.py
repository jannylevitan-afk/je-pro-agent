from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SeedProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: str
    handle: str


class AudienceSegmentSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route_to: str
    seed_profiles: list[SeedProfile] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_seed_profiles(self) -> "AudienceSegmentSeed":
        if not self.seed_profiles:
            raise ValueError("seed_profiles must contain at least one profile")
        return self


class ContentThemeSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route_to: str


class SeedConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience_segments: list[AudienceSegmentSeed] = Field(default_factory=list)
    content_theme_sources: list[ContentThemeSource] = Field(default_factory=list)


def load_seed_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return SeedConfig.model_validate(data).model_dump()
