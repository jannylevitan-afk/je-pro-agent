from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


_NOTION_ID_PATTERN = re.compile(r"([0-9a-fA-F]{32}|[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})")


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    notion_api_key: str
    anthropic_api_key: str
    notion_parent_page_id: str | None = None
    notion_parent_page_url: str | None = None
    notion_api_base: str = "https://api.notion.com/v1"
    notion_version: str = "2022-06-28"
    anthropic_api_base: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"
    anthropic_model: str = "claude-sonnet-4-20250514"
    request_timeout_seconds: float = 30.0
    source_feed_url: str | None = None
    kmd_root: str = "knowledge/kmd"

    def __post_init__(self) -> None:
        notion_api_key = self.notion_api_key.strip()
        anthropic_api_key = self.anthropic_api_key.strip()
        notion_parent_page_url = self.notion_parent_page_url.strip() if self.notion_parent_page_url else None
        notion_parent_page_id = self.notion_parent_page_id.strip() if self.notion_parent_page_id else None

        if not notion_api_key:
            raise ValueError("notion_api_key must not be empty")
        if not anthropic_api_key:
            raise ValueError("anthropic_api_key must not be empty")

        if notion_parent_page_id is None and notion_parent_page_url is None:
            raise ValueError("Either notion_parent_page_id or notion_parent_page_url must be provided")

        resolved_page_id = _normalize_notion_id(notion_parent_page_id or _extract_notion_id(notion_parent_page_url))

        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be greater than zero")
        kmd_root = self.kmd_root.strip() or "knowledge/kmd"

        object.__setattr__(self, "notion_api_key", notion_api_key)
        object.__setattr__(self, "anthropic_api_key", anthropic_api_key)
        object.__setattr__(self, "notion_parent_page_url", notion_parent_page_url)
        object.__setattr__(self, "notion_parent_page_id", resolved_page_id)
        object.__setattr__(self, "anthropic_model", self.anthropic_model.strip() or "claude-sonnet-4-20250514")
        object.__setattr__(self, "kmd_root", kmd_root)


def load_runtime_settings(
    environ: dict[str, str] | None = None,
    env_file: str | Path | None = None,
) -> RuntimeSettings:
    env_values = _read_env_file(Path(env_file) if env_file is not None else Path(".env.local"))
    merged = env_values | dict(environ or os.environ)

    return RuntimeSettings(
        notion_api_key=merged.get("NOTION_API_KEY", ""),
        notion_parent_page_id=merged.get("NOTION_PARENT_PAGE_ID"),
        notion_parent_page_url=merged.get("NOTION_PARENT_PAGE_URL"),
        notion_api_base=merged.get("NOTION_API_BASE", "https://api.notion.com/v1"),
        notion_version=merged.get("NOTION_VERSION", "2022-06-28"),
        anthropic_api_key=merged.get("ANTHROPIC_API_KEY", ""),
        anthropic_api_base=merged.get("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1"),
        anthropic_version=merged.get("ANTHROPIC_VERSION", "2023-06-01"),
        anthropic_model=merged.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        request_timeout_seconds=float(merged.get("CONTENT_ENGINE_REQUEST_TIMEOUT_SECONDS", "30.0")),
        source_feed_url=merged.get("CONTENT_ENGINE_SOURCE_FEED_URL"),
        kmd_root=merged.get("CONTENT_ENGINE_KMD_ROOT", "knowledge/kmd"),
    )


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        values[key.strip()] = _strip_quotes(raw_value.strip())
    return values


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _extract_notion_id(value: str | None) -> str:
    if value is None:
        raise ValueError("Notion page id could not be derived from empty value")
    match = _NOTION_ID_PATTERN.search(value)
    if match is None:
        raise ValueError("Notion page id could not be derived from value")
    return match.group(1)


def _normalize_notion_id(value: str) -> str:
    raw = value.replace("-", "").lower()
    if len(raw) != 32:
        raise ValueError("Notion page id must contain 32 hexadecimal characters")
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
