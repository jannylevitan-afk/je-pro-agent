from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from content_engine.models.approval import ApprovalResult, CalendarItem, DraftRecord, OrchestrationEvent
from content_engine.models.workflow_b import BriefRecord
from content_engine.notion.payloads import (
    build_brief_properties,
    build_calendar_properties,
    build_draft_properties,
    build_orchestration_event_properties,
)


class NotionClientLike(Protocol):
    def create_database_page(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        ...

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        ...

    def query_database(self, database_id: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class ApprovalNotionTargets:
    drafts_database_id: str
    briefs_database_id: str
    calendar_database_id: str
    events_database_id: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("drafts_database_id", self.drafts_database_id),
            ("briefs_database_id", self.briefs_database_id),
            ("calendar_database_id", self.calendar_database_id),
            ("events_database_id", self.events_database_id),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class ApprovalSyncResult:
    draft_page_id: str
    next_draft_page_id: str | None
    brief_page_id: str | None
    calendar_page_id: str | None
    event_page_ids: list[str]


def upsert_draft(
    client: NotionClientLike,
    database_id: str,
    draft: DraftRecord,
) -> dict[str, Any]:
    return _upsert_by_external_id(
        client=client,
        database_id=database_id,
        external_id_property="Draft ID",
        external_id_value=draft.draft_id,
        properties=build_draft_properties(draft),
    )


def upsert_brief(
    client: NotionClientLike,
    database_id: str,
    brief: BriefRecord,
) -> dict[str, Any]:
    return _upsert_by_external_id(
        client=client,
        database_id=database_id,
        external_id_property="Brief ID",
        external_id_value=brief.brief_id,
        properties=build_brief_properties(brief),
    )


def create_calendar_item(
    client: NotionClientLike,
    database_id: str,
    calendar_item: CalendarItem,
) -> dict[str, Any]:
    return client.create_database_page(
        database_id=database_id,
        properties=build_calendar_properties(calendar_item),
    )


def create_orchestration_event(
    client: NotionClientLike,
    database_id: str,
    event: OrchestrationEvent,
) -> dict[str, Any]:
    return client.create_database_page(
        database_id=database_id,
        properties=build_orchestration_event_properties(event),
    )


def sync_approval_result(
    client: NotionClientLike,
    targets: ApprovalNotionTargets,
    result: ApprovalResult,
) -> ApprovalSyncResult:
    draft_response = upsert_draft(
        client=client,
        database_id=targets.drafts_database_id,
        draft=result.updated_draft,
    )
    draft_page_id = _extract_page_id(draft_response)

    next_draft_page_id: str | None = None
    if result.next_draft is not None:
        next_draft_response = upsert_draft(
            client=client,
            database_id=targets.drafts_database_id,
            draft=result.next_draft,
        )
        next_draft_page_id = _extract_page_id(next_draft_response)

    brief_page_id: str | None = None
    if result.brief_update is not None:
        brief_response = upsert_brief(
            client=client,
            database_id=targets.briefs_database_id,
            brief=result.brief_update,
        )
        brief_page_id = _extract_page_id(brief_response)

    calendar_page_id: str | None = None
    if result.calendar_item is not None:
        calendar_response = create_calendar_item(
            client=client,
            database_id=targets.calendar_database_id,
            calendar_item=result.calendar_item,
        )
        calendar_page_id = _extract_page_id(calendar_response)

    event_page_ids: list[str] = []
    for event in result.events:
        event_response = create_orchestration_event(
            client=client,
            database_id=targets.events_database_id,
            event=event,
        )
        event_page_ids.append(_extract_page_id(event_response))

    return ApprovalSyncResult(
        draft_page_id=draft_page_id,
        next_draft_page_id=next_draft_page_id,
        brief_page_id=brief_page_id,
        calendar_page_id=calendar_page_id,
        event_page_ids=event_page_ids,
    )


def _upsert_by_external_id(
    client: NotionClientLike,
    database_id: str,
    external_id_property: str,
    external_id_value: str,
    properties: dict[str, Any],
) -> dict[str, Any]:
    query = _external_id_query(
        property_name=external_id_property,
        value=external_id_value,
    )
    query_response = client.query_database(
        database_id=database_id,
        query=query,
    )
    raw_results = query_response.get("results", [])
    if not isinstance(raw_results, list):
        raise ValueError("Notion query response must contain a list in `results`")

    if len(raw_results) > 1:
        raise ValueError(
            f"Multiple pages found for {external_id_property}={external_id_value}",
        )
    if len(raw_results) == 1:
        existing_page_id = _extract_page_id(raw_results[0])
        return client.update_page(
            page_id=existing_page_id,
            properties=properties,
        )
    return client.create_database_page(
        database_id=database_id,
        properties=properties,
    )


def _external_id_query(property_name: str, value: str) -> dict[str, Any]:
    return {
        "filter": {
            "property": property_name,
            "rich_text": {"equals": value},
        },
        "page_size": 2,
    }


def _extract_page_id(payload: dict[str, Any]) -> str:
    page_id = payload.get("id")
    if not isinstance(page_id, str) or page_id == "":
        raise ValueError("Notion page payload does not contain a valid `id`")
    return page_id
