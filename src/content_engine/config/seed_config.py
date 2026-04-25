from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from content_engine.collectors.native import NativeSourceTarget


@dataclass(frozen=True, slots=True)
class DiscoveryQuery:
    query: str
    content_theme: str
    audience_segment: str
    platform_target: str
    route_to: str
    seed_source_names: list[str]


class SeedProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: str
    handle: str
    why: str | None = None


class DiscoveryCriteria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bio_keywords: list[str] = Field(default_factory=list)
    geo: list[str] = Field(default_factory=list)
    follower_range: str | None = None
    content_signals: list[str] = Field(default_factory=list)


class AudienceSegmentSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route_to: str
    seed_profiles: list[SeedProfile] = Field(default_factory=list)
    role_in_funnel: str | None = None
    discovery_criteria: DiscoveryCriteria | None = None

    @model_validator(mode="after")
    def validate_seed_profiles(self) -> "AudienceSegmentSeed":
        if not self.seed_profiles:
            raise ValueError("seed_profiles must contain at least one profile")
        return self


class ContentThemeSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route_to: str
    title: str | None = None
    audience_segments: list[str] = Field(default_factory=list)
    primary_audience_segment: str | None = None
    content_pillars: list[str] = Field(default_factory=list)
    narrative_types: list[str] = Field(default_factory=list)
    suggested_registers: list[str] = Field(default_factory=list)
    collect_fields: list[str] = Field(default_factory=list)
    discovery_keywords: list[str] = Field(default_factory=list)
    similar_source_targets: list[str] = Field(default_factory=list)
    sources: list["CuratedSource"] = Field(default_factory=list)


class CuratedSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: str
    source_name: str
    source_url: str
    collect_for: str
    handle: str | None = None
    audience_segment: str | None = None
    content_theme: str | None = None
    source_role: str = "seed"


class SeedConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience_segments: list[AudienceSegmentSeed] = Field(default_factory=list)
    content_theme_sources: list[ContentThemeSource] = Field(default_factory=list)


def load_seed_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return SeedConfig.model_validate(data).model_dump()


def build_native_source_targets(config: dict[str, Any] | SeedConfig) -> list[NativeSourceTarget]:
    seed_config = config if isinstance(config, SeedConfig) else SeedConfig.model_validate(config)
    targets: list[NativeSourceTarget] = []
    for theme in seed_config.content_theme_sources:
        theme_audience = theme.primary_audience_segment or _first_or_default(
            theme.audience_segments,
            "developer_investor",
        )
        for source in theme.sources:
            targets.append(
                NativeSourceTarget(
                    platform=source.platform,  # type: ignore[arg-type]
                    handle=source.handle or _handle_from_url(source.source_url),
                    source_url=source.source_url,
                    source_name=source.source_name,
                    audience_segment=source.audience_segment or theme_audience,
                    content_theme=source.content_theme or theme.name,
                )
            )
    return targets


def load_native_source_targets(path: Path) -> list[NativeSourceTarget]:
    return build_native_source_targets(SeedConfig.model_validate(load_seed_config(path)))


def build_discovery_queries(config: dict[str, Any] | SeedConfig) -> list[DiscoveryQuery]:
    seed_config = config if isinstance(config, SeedConfig) else SeedConfig.model_validate(config)
    queries: list[DiscoveryQuery] = []
    for theme in seed_config.content_theme_sources:
        audience = theme.primary_audience_segment or _first_or_default(theme.audience_segments, "developer_investor")
        seed_source_names = [source.source_name for source in theme.sources]
        for platform_target in theme.similar_source_targets:
            for keyword in theme.discovery_keywords:
                queries.append(
                    DiscoveryQuery(
                        query=_build_discovery_query(keyword, platform_target, seed_source_names),
                        content_theme=theme.name,
                        audience_segment=audience,
                        platform_target=platform_target,
                        route_to=theme.route_to,
                        seed_source_names=seed_source_names,
                    )
                )
    return queries


def _first_or_default(values: list[str], default: str) -> str:
    return values[0] if values else default


def _handle_from_url(url: str) -> str:
    normalized = url.rstrip("/")
    if "instagram.com/" in normalized:
        return normalized.rsplit("/", 1)[-1]
    if "t.me/" in normalized:
        return f"@{normalized.rsplit('/', 1)[-1]}"
    host = normalized.split("//", 1)[-1].split("/", 1)[0]
    path = normalized.split("//", 1)[-1].split("/", 1)[1:] or [host]
    suffix = path[0].replace("/", "-") if path else host
    return suffix or host


def _build_discovery_query(keyword: str, platform_target: str, seed_source_names: list[str]) -> str:
    seeds = ", ".join(seed_source_names[:3])
    if seeds:
        return f"{keyword} similar to {seeds} for {platform_target}"
    return f"{keyword} for {platform_target}"
