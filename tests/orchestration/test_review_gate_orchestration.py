from collections.abc import Sequence

from content_engine.models.approval import ReviewAction
from content_engine.notion.sync import ApprovalNotionTargets
from content_engine.orchestration.review_gate import orchestrate_review_outcome
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

    def query_database(self, database_id: str, query: dict | None = None) -> dict:
        if not self._query_results:
            raise AssertionError("Unexpected query_database call")
        return self._query_results.pop(0)

    def create_database_page(self, database_id: str, properties: dict) -> dict:
        if not self._create_results:
            raise AssertionError("Unexpected create_database_page call")
        return self._create_results.pop(0)

    def update_page(self, page_id: str, properties: dict) -> dict:
        if not self._update_results:
            raise AssertionError("Unexpected update_page call")
        return self._update_results.pop(0)


def test_orchestrate_review_outcome_approved(linkedin_draft_record) -> None:
    submitted, _ = submit_for_review(
        linkedin_draft_record,
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
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

    orchestrated = orchestrate_review_outcome(
        client=client,
        targets=targets,
        result=result,
    )

    assert orchestrated.notion_sync.calendar_page_id == "calendar_page_1"
    assert orchestrated.n8n_envelope["route"] == "approved"
    assert "Ready to publish" in orchestrated.telegram_notification["message"]


def test_orchestrate_review_outcome_rewrite(linkedin_draft_record) -> None:
    submitted, _ = submit_for_review(
        linkedin_draft_record,
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
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

    orchestrated = orchestrate_review_outcome(
        client=client,
        targets=targets,
        result=result,
    )

    assert orchestrated.notion_sync.next_draft_page_id == "draft_next_page"
    assert orchestrated.n8n_envelope["route"] == "needs_rewrite"
    assert "version 2" in orchestrated.telegram_notification["message"]
