from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from content_engine.knowledge.kmd import KnowledgeStore
from content_engine.orchestration.live_pipeline import (
    LivePipelineItemResult,
    SourceCollector,
    WorkflowWriter,
    run_collector_cycle,
)
from content_engine.services.analyst import WorkflowAnalyst
from content_engine.orchestration.targets import LivePipelineTargets


_LOCAL_TARGETS = LivePipelineTargets(
    sources_database_id="db_sources",
    insights_database_id="db_insights",
    ideas_database_id="db_ideas",
    briefs_database_id="db_briefs",
    drafts_database_id="db_drafts",
    events_database_id="db_events",
    scripts_database_id="db_scripts",
    filming_cards_database_id="db_filming",
)

_DATABASE_LABELS = {
    "db_sources": "sources",
    "db_insights": "insights",
    "db_ideas": "ideas",
    "db_briefs": "briefs",
    "db_drafts": "drafts",
    "db_events": "events",
    "db_scripts": "scripts",
    "db_filming": "filming_cards",
}


@dataclass(frozen=True, slots=True)
class LocalPipelineDryRunReport:
    item_results: list[LivePipelineItemResult]
    database_snapshots: dict[str, list[dict[str, Any]]]


class InMemoryNotionClient:
    def __init__(self) -> None:
        self._pages_by_database: dict[str, list[dict[str, Any]]] = {}
        self._page_index: dict[str, dict[str, Any]] = {}
        self._database_counters: dict[str, int] = {}

    def query_database(self, database_id: str, query: dict | None = None) -> dict:
        pages = self._pages_by_database.get(database_id, [])
        if query is None:
            return {"results": [self._page_stub(page) for page in pages]}

        filter_payload = query.get("filter", {})
        if not isinstance(filter_payload, dict):
            return {"results": [self._page_stub(page) for page in pages]}

        property_name = filter_payload.get("property")
        rich_text_filter = filter_payload.get("rich_text")
        if not isinstance(property_name, str) or not isinstance(rich_text_filter, dict):
            return {"results": [self._page_stub(page) for page in pages]}

        expected = rich_text_filter.get("equals")
        filtered = [
            self._page_stub(page)
            for page in pages
            if _extract_rich_text_content(page["properties"].get(property_name)) == expected
        ]
        return {"results": filtered}

    def create_database_page(self, database_id: str, properties: dict) -> dict:
        page_id = self._next_page_id(database_id)
        page = {
            "id": page_id,
            "object": "page",
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        self._pages_by_database.setdefault(database_id, []).append(page)
        self._page_index[page_id] = page
        return {"id": page_id, "object": "page", "properties": properties}

    def update_page(self, page_id: str, properties: dict) -> dict:
        page = self._page_index[page_id]
        page["properties"] = properties
        return {"id": page_id, "object": "page", "properties": properties}

    def snapshot(self) -> dict[str, list[dict[str, Any]]]:
        return {
            _DATABASE_LABELS[database_id]: [
                {name: _flatten_property(value) for name, value in page["properties"].items()}
                for page in pages
            ]
            for database_id, pages in self._pages_by_database.items()
            if database_id in _DATABASE_LABELS
        }

    def _next_page_id(self, database_id: str) -> str:
        next_value = self._database_counters.get(database_id, 0) + 1
        self._database_counters[database_id] = next_value
        return f"{database_id}_page_{next_value}"

    @staticmethod
    def _page_stub(page: dict[str, Any]) -> dict[str, Any]:
        return {"id": page["id"], "properties": page["properties"]}


def run_local_pipeline_dry_run(
    *,
    collector: SourceCollector,
    writer: WorkflowWriter | None,
    analyst: WorkflowAnalyst | None = None,
    verified_facts: set[str],
    submitted_at: str,
    knowledge_store: KnowledgeStore | None = None,
) -> LocalPipelineDryRunReport:
    client = InMemoryNotionClient()
    item_results = run_collector_cycle(
        collector=collector,
        client=client,
        targets=_LOCAL_TARGETS,
        verified_facts=verified_facts,
        submitted_at=submitted_at,
        writer=writer,
        analyst=analyst,
        knowledge_store=knowledge_store,
    )
    return LocalPipelineDryRunReport(
        item_results=item_results,
        database_snapshots=client.snapshot(),
    )


def _flatten_property(payload: dict[str, Any]) -> Any:
    if "title" in payload:
        return _extract_rich_text_content({"rich_text": payload["title"]})
    if "rich_text" in payload:
        return _extract_rich_text_content(payload)
    if "select" in payload:
        selected = payload["select"]
        if isinstance(selected, dict):
            return selected.get("name")
        return None
    if "number" in payload:
        return payload["number"]
    if "checkbox" in payload:
        return payload["checkbox"]
    if "date" in payload:
        date_value = payload["date"]
        if isinstance(date_value, dict):
            return date_value.get("start")
        return None
    if "url" in payload:
        return payload["url"]
    if "relation" in payload:
        return payload["relation"]
    return payload


def _extract_rich_text_content(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    rich_text = payload.get("rich_text")
    if not isinstance(rich_text, list) or not rich_text:
        return None

    parts: list[str] = []
    for item in rich_text:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, dict) and isinstance(text.get("content"), str):
            parts.append(text["content"])
    return "".join(parts) if parts else None
