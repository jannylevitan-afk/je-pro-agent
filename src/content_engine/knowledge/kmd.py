from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from content_engine.knowledge.research_dependencies import (
    WorkflowName,
    resolve_research_dependencies,
)
from content_engine.models.source_item import SourceItem


class KnowledgeStore(Protocol):
    def write_source_material(self, item: SourceItem, *, workflow: WorkflowName) -> Path:
        ...


class MarkdownKnowledgeStore:
    def __init__(self, root: str | Path = "knowledge/kmd") -> None:
        self.root = Path(root)

    def write_source_material(self, item: SourceItem, *, workflow: WorkflowName) -> Path:
        dependencies = resolve_research_dependencies(item, workflow=workflow)
        path = (
            self.root
            / workflow
            / _slug(item.audience_segment)
            / _slug(dependencies.content_theme)
            / f"{_slug(item.item_id)}.kmd.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_kmd_material(item, workflow=workflow), encoding="utf-8")
        return path


def render_kmd_material(item: SourceItem, *, workflow: WorkflowName) -> str:
    dependencies = resolve_research_dependencies(item, workflow=workflow)
    frontmatter = {
        "workflow": workflow,
        "item_id": item.item_id,
        "source_type": item.source_type,
        "source_name": item.source_name,
        "source_url": item.source_url,
        "published_at": item.published_at,
        "collected_at": item.collected_at,
        "audience_segment": item.audience_segment,
        "content_theme": dependencies.content_theme,
        "routing_decision": item.routing_decision,
        "routing_confidence": item.routing_confidence,
    }

    sections = [
        "---",
        *_format_frontmatter(frontmatter),
        "---",
        "",
        f"# {workflow} material - {item.item_id}",
        "",
        "## Search Dependencies",
        _bullet_list(asdict(dependencies), include_keys=True),
        "",
        "## Evidence",
        _bullet_list(
            {
                "source URL": item.source_url,
                "timestamp": item.published_at or item.collected_at,
                "raw excerpt": _excerpt(item.transcript_text),
                "confidence score": item.routing_confidence,
            },
            include_keys=True,
        ),
        "",
        "## Source Note",
        _bullet_list(
            {
                "source type": item.source_type,
                "source name": item.source_name,
                "topic guess": dependencies.content_theme,
                "audience guess": item.audience_segment,
                "content type guess": "video" if item.media_urls else "text",
                "engagement signals": item.engagement_signals,
                "media urls": item.media_urls,
            },
            include_keys=True,
        ),
        "",
        "## Raw Text",
        item.transcript_text.strip(),
        "",
        "## Writer Context",
        _bullet_list(dependencies.writer_context),
        "",
    ]
    return "\n".join(sections)


def _format_frontmatter(values: dict[str, object]) -> list[str]:
    return [f"{key}: {_frontmatter_value(value)}" for key, value in values.items()]


def _frontmatter_value(value: object) -> str:
    if isinstance(value, str):
        return value.replace("\n", " ")
    return str(value)


def _bullet_list(value: object, *, include_keys: bool = False) -> str:
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, list):
                lines.append(f"- {key}: {', '.join(str(part) for part in item)}")
            elif isinstance(item, dict):
                nested = ", ".join(f"{nested_key}={nested_value}" for nested_key, nested_value in item.items())
                lines.append(f"- {key}: {nested}")
            else:
                lines.append(f"- {key}: {item}")
        return "\n".join(lines)
    if isinstance(value, list):
        if include_keys:
            return "\n".join(f"- value: {item}" for item in value)
        return "\n".join(f"- {item}" for item in value)
    return f"- {value}"


def _excerpt(text: str, limit: int = 360) -> str:
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


def _slug(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9а-яё_-]+", "_", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "unknown"
