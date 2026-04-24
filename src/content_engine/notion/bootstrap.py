from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from content_engine.notion.schema_defs import (
    BRIEFS_DB_SCHEMA,
    DRAFTS_DB_SCHEMA,
    FILMING_CARDS_SCHEMA,
    IDEAS_DB_SCHEMA,
    INSIGHTS_DB_SCHEMA,
    ORCHESTRATION_EVENT_SCHEMA,
    SCRIPTS_QUEUE_SCHEMA,
    SOURCES_DB_SCHEMA,
)
from content_engine.orchestration.targets import LivePipelineTargets


class NotionBootstrapClient(Protocol):
    def search(self, query: str) -> dict[str, Any]:
        ...

    def create_database(self, parent_page_id: str, title: str, properties: dict[str, Any]) -> dict[str, Any]:
        ...

    def retrieve_database(self, database_id: str) -> dict[str, Any]:
        ...

    def update_database(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class DatabaseSpec:
    title: str
    schema: dict[str, str]


_LIVE_PIPELINE_DATABASES: list[tuple[str, DatabaseSpec]] = [
    ("sources_database_id", DatabaseSpec("Content Engine Sources", SOURCES_DB_SCHEMA)),
    ("insights_database_id", DatabaseSpec("Content Engine Insights", INSIGHTS_DB_SCHEMA)),
    ("ideas_database_id", DatabaseSpec("Content Engine Ideas", IDEAS_DB_SCHEMA)),
    ("briefs_database_id", DatabaseSpec("Content Engine Briefs", BRIEFS_DB_SCHEMA)),
    ("drafts_database_id", DatabaseSpec("Content Engine Drafts", DRAFTS_DB_SCHEMA)),
    ("events_database_id", DatabaseSpec("Content Engine Events", ORCHESTRATION_EVENT_SCHEMA)),
    ("scripts_database_id", DatabaseSpec("Content Engine Scripts", SCRIPTS_QUEUE_SCHEMA)),
    ("filming_cards_database_id", DatabaseSpec("Content Engine Filming Cards", FILMING_CARDS_SCHEMA)),
]


def ensure_live_pipeline_targets(
    client: NotionBootstrapClient,
    parent_page_id: str,
) -> LivePipelineTargets:
    database_ids: dict[str, str] = {}
    for field_name, spec in _LIVE_PIPELINE_DATABASES:
        database = _ensure_database(client, parent_page_id, spec)
        database_ids[field_name] = _extract_id(database)
    return LivePipelineTargets(**database_ids)


def _ensure_database(
    client: NotionBootstrapClient,
    parent_page_id: str,
    spec: DatabaseSpec,
) -> dict[str, Any]:
    existing = _find_database(client, parent_page_id, spec.title)
    expected_properties = _build_database_properties(spec.schema)
    if existing is None:
        return client.create_database(parent_page_id, spec.title, expected_properties)

    database_id = _extract_id(existing)
    retrieved = client.retrieve_database(database_id)
    current_properties = retrieved.get("properties", {})
    missing_properties = _missing_properties(current_properties, spec.schema)
    if missing_properties:
        client.update_database(database_id, missing_properties)
    return existing


def _find_database(
    client: NotionBootstrapClient,
    parent_page_id: str,
    title: str,
) -> dict[str, Any] | None:
    response = client.search(title)
    results = response.get("results")
    if not isinstance(results, list):
        return None

    normalized_parent_id = parent_page_id.replace("-", "")
    for result in results:
        if not isinstance(result, dict):
            continue
        if result.get("object") not in {"database", "data_source"}:
            continue
        parent = result.get("parent", {})
        if not isinstance(parent, dict):
            continue
        result_parent_id = str(parent.get("page_id", "")).replace("-", "")
        if result_parent_id != normalized_parent_id:
            continue
        if _extract_title_text(result) == title:
            return result
    return None


def _extract_title_text(result: dict[str, Any]) -> str:
    title_items = result.get("title")
    if not isinstance(title_items, list):
        return ""
    return "".join(
        item.get("plain_text", "")
        for item in title_items
        if isinstance(item, dict) and isinstance(item.get("plain_text"), str)
    )


def _missing_properties(
    current_properties: dict[str, Any],
    expected_schema: dict[str, str],
) -> dict[str, Any]:
    missing: dict[str, Any] = {}
    for name, property_type in expected_schema.items():
        current = current_properties.get(name)
        if current is None:
            missing[name] = _property_definition(property_type)
            continue
        if not isinstance(current, dict):
            raise ValueError(f"Unexpected Notion property payload for {name}")
        current_type = current.get("type")
        if current_type != property_type:
            raise ValueError(
                f"Notion property {name} has type {current_type}, expected {property_type}"
            )
    return missing


def _build_database_properties(schema: dict[str, str]) -> dict[str, Any]:
    return {
        name: _property_definition(property_type)
        for name, property_type in schema.items()
    }


def _property_definition(property_type: str) -> dict[str, Any]:
    if property_type == "title":
        return {"title": {}}
    if property_type == "rich_text":
        return {"rich_text": {}}
    if property_type == "select":
        return {"select": {"options": []}}
    if property_type == "number":
        return {"number": {"format": "number"}}
    if property_type == "checkbox":
        return {"checkbox": {}}
    if property_type == "date":
        return {"date": {}}
    if property_type == "url":
        return {"url": {}}
    raise ValueError(f"Unsupported Notion property type: {property_type}")


def _extract_id(payload: dict[str, Any]) -> str:
    value = payload.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("Notion database payload must include an id")
    return value
