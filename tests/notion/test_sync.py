from collections.abc import Sequence

import pytest

from content_engine.models.approval import ReviewAction
from content_engine.notion.sync import (
    ApprovalNotionTargets,
    ApprovalSyncResult,
    sync_approval_result,
    upsert_draft,
)
from content_engine.services.approval import apply_review_action, submit_for_review


class StubNotionClient:
    def __init__(
        self,
        query_results: Sequence[dict] | None = None,
        create_results: Sequence[dict] | None = None,
        update_results: Sequence[dict] | None = None,
    ) -> None:
        self._query_results = list(query_results or [])
        self._create_results = list(create_results or [])
        self._update_results = list(update_results or [])
        self.query_calls: list[tuple[str, dict]] = []
        self.create_calls: list[tuple[str, dict]] = []
        self.update_calls: list[tuple[str, dict]] = []

    def query_database(self, database_id: str, query: dict | None = None) -> dict:
        self.query_calls.append((database_id, query or {}))
        if not self._query_results:
            raise AssertionError("Unexpected query_database call")
        return self._query_results.pop(0)

    def create_database_page(self, database_id: str, properties: dict) -> dict:
        self.create_calls.append((database_id, properties))
        if not self._create_results:
            raise AssertionError("Unexpected create_database_page call")
        return self._create_results.pop(0)

    def update_page(self, page_id: str, properties: dict) -> dict:
        self.update_calls.append((page_id, properties))
        if not self._update_results:
            raise AssertionError("Unexpected update_page call")
        return self._update_results.pop(0)


def test_upsert_draft_creates_page_when_record_is_missing(linkedin_draft_record) -> None:
    client = StubNotionClient(
        query_results=[{"results": []}],
        create_results=[{"id": "new_page"}],
    )

    response = upsert_draft(
        client=client,
        database_id="db_drafts",
        draft=linkedin_draft_record,
    )

    assert response["id"] == "new_page"
    assert client.query_calls[0][0] == "db_drafts"
    assert client.query_calls[0][1]["filter"]["property"] == "Draft ID"
    assert client.query_calls[0][1]["filter"]["rich_text"]["equals"] == "dr_001"
    assert client.create_calls[0][0] == "db_drafts"
    assert client.update_calls == []


def test_upsert_draft_updates_existing_page(linkedin_draft_record) -> None:
    client = StubNotionClient(
        query_results=[{"results": [{"id": "page_123"}]}],
        update_results=[{"id": "page_123"}],
    )

    response = upsert_draft(
        client=client,
        database_id="db_drafts",
        draft=linkedin_draft_record,
    )

    assert response["id"] == "page_123"
    assert client.create_calls == []
    assert client.update_calls[0][0] == "page_123"


def test_upsert_draft_raises_when_multiple_matches_found(linkedin_draft_record) -> None:
    client = StubNotionClient(
        query_results=[{"results": [{"id": "page_1"}, {"id": "page_2"}]}],
    )

    with pytest.raises(ValueError, match="Multiple pages found"):
        upsert_draft(
            client=client,
            database_id="db_drafts",
            draft=linkedin_draft_record,
        )


def test_sync_approval_result_approved_flow(linkedin_draft_record) -> None:
    submitted, _ = submit_for_review(
        linkedin_draft_record,
        submitted_at="2026-04-24T09:00:00Z",
    )
    approval_result = apply_review_action(
        submitted,
        ReviewAction(
            decision="approved",
            decided_at="2026-04-24T09:05:00Z",
        ),
    )
    client = StubNotionClient(
        query_results=[{"results": []}],
        create_results=[
            {"id": "draft_page_1"},
            {"id": "calendar_page_1"},
            {"id": "event_page_1"},
            {"id": "event_page_2"},
        ],
    )
    targets = ApprovalNotionTargets(
        drafts_database_id="db_drafts",
        briefs_database_id="db_briefs",
        calendar_database_id="db_calendar",
        events_database_id="db_events",
    )

    sync_result = sync_approval_result(
        client=client,
        targets=targets,
        result=approval_result,
    )

    assert sync_result == ApprovalSyncResult(
        draft_page_id="draft_page_1",
        next_draft_page_id=None,
        brief_page_id=None,
        calendar_page_id="calendar_page_1",
        event_page_ids=["event_page_1", "event_page_2"],
    )
    assert client.query_calls[0][0] == "db_drafts"
    assert [call[0] for call in client.create_calls] == [
        "db_drafts",
        "db_calendar",
        "db_events",
        "db_events",
    ]


def test_sync_approval_result_rewrite_flow_creates_next_draft(linkedin_draft_record) -> None:
    submitted, _ = submit_for_review(
        linkedin_draft_record,
        submitted_at="2026-04-24T09:00:00Z",
    )
    approval_result = apply_review_action(
        submitted,
        ReviewAction(
            decision="needs_rewrite",
            notes="Make opening less formal.",
            rewritten_text_ru="Russian master rewritten",
            rewritten_text_en="English publish rewritten",
            decided_at="2026-04-24T09:10:00Z",
        ),
    )
    client = StubNotionClient(
        query_results=[{"results": []}, {"results": []}],
        create_results=[
            {"id": "draft_archived_page"},
            {"id": "draft_next_page"},
            {"id": "event_page_1"},
            {"id": "event_page_2"},
        ],
    )
    targets = ApprovalNotionTargets(
        drafts_database_id="db_drafts",
        briefs_database_id="db_briefs",
        calendar_database_id="db_calendar",
        events_database_id="db_events",
    )

    sync_result = sync_approval_result(
        client=client,
        targets=targets,
        result=approval_result,
    )

    assert sync_result.draft_page_id == "draft_archived_page"
    assert sync_result.next_draft_page_id == "draft_next_page"
    assert sync_result.calendar_page_id is None
    assert sync_result.brief_page_id is None
    assert sync_result.event_page_ids == ["event_page_1", "event_page_2"]
