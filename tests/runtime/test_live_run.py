import pytest

from content_engine.knowledge.kmd import MarkdownKnowledgeStore
from content_engine.runtime.live_run import (
    StaticSourceCollector,
    dispatch_video_gate_payloads,
    resolve_anthropic_model,
    run_configured_live_pipeline,
)
from content_engine.runtime.settings import RuntimeSettings
from content_engine.notion import NotionHTTPError


class StubRuntimeClient:
    def __init__(
        self,
        *,
        search_results: list[dict],
        database_create_results: list[dict],
        page_query_results: list[dict],
        page_create_results: list[dict],
    ) -> None:
        self._search_results = list(search_results)
        self._database_create_results = list(database_create_results)
        self._page_query_results = list(page_query_results)
        self._page_create_results = list(page_create_results)
        self.database_create_calls: list[tuple[str, str, dict]] = []
        self.page_create_calls: list[tuple[str, dict]] = []
        self.retrieve_page_calls: list[str] = []

    def search(self, query: str) -> dict:
        if not self._search_results:
            raise AssertionError("Unexpected search call")
        return self._search_results.pop(0)

    def create_database(self, parent_page_id: str, title: str, properties: dict) -> dict:
        self.database_create_calls.append((parent_page_id, title, properties))
        if not self._database_create_results:
            raise AssertionError("Unexpected create_database call")
        return self._database_create_results.pop(0)

    def retrieve_database(self, database_id: str) -> dict:
        raise AssertionError("retrieve_database should not be called for missing databases")

    def update_database(self, database_id: str, properties: dict) -> dict:
        raise AssertionError("update_database should not be called for missing databases")

    def retrieve_page(self, page_id: str) -> dict:
        self.retrieve_page_calls.append(page_id)
        return {"id": page_id, "object": "page"}

    def query_database(self, database_id: str, query: dict | None = None) -> dict:
        if not self._page_query_results:
            raise AssertionError("Unexpected query_database call")
        return self._page_query_results.pop(0)

    def create_database_page(self, database_id: str, properties: dict) -> dict:
        self.page_create_calls.append((database_id, properties))
        if not self._page_create_results:
            raise AssertionError("Unexpected create_database_page call")
        return self._page_create_results.pop(0)

    def update_page(self, page_id: str, properties: dict) -> dict:
        raise AssertionError("update_page should not be called in this test")


class FakeWriter:
    def write_video_script(self, *, item, title: str, hook: str, body_points: list[str], cta: str) -> str:
        return "Anthropic video script"

    def write_workflow_b_draft(self, *, item, insight, decision, brief):
        class Draft:
            draft_text_ru = "Anthropic Russian draft"
            draft_text_en = "Anthropic English draft"

        return Draft()


class StubModelDiscoveryClient:
    def __init__(self, model_ids: list[str]) -> None:
        self.model_ids = model_ids

    def list_models(self) -> dict:
        return {"data": [{"id": model_id} for model_id in self.model_ids]}


class StubN8NClient:
    def __init__(self) -> None:
        self.sent_payloads: list[dict] = []

    def send(self, payload: dict) -> dict:
        self.sent_payloads.append(payload)
        return {"ok": True}


def test_run_configured_live_pipeline_bootstraps_processes_items_and_writes_kmd(tmp_path, video_source_item) -> None:
    client = StubRuntimeClient(
        search_results=[{"results": []}] * 8,
        database_create_results=[
            {"id": "db_sources"},
            {"id": "db_insights"},
            {"id": "db_ideas"},
            {"id": "db_briefs"},
            {"id": "db_drafts"},
            {"id": "db_events"},
            {"id": "db_scripts"},
            {"id": "db_filming"},
        ],
        page_query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        page_create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    settings = RuntimeSettings(
        notion_api_key="notion-token",
        notion_parent_page_id="34b2a925815780b8bd08d56c7e1293cf",
        anthropic_api_key="anthropic-token",
    )

    results = run_configured_live_pipeline(
        settings=settings,
        notion_client=client,
        writer=FakeWriter(),
        collector=StaticSourceCollector([video_source_item]),
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
        knowledge_store=MarkdownKnowledgeStore(tmp_path),
    )

    assert results[0].script_page_id == "script_page_1"
    assert len(results[0].knowledge_file_paths) == 2
    assert client.database_create_calls[0][1] == "Content Engine Sources"
    assert client.page_create_calls[1][1]["Script text"]["rich_text"][0]["text"]["content"] == "Anthropic video script"


def test_run_configured_live_pipeline_dispatches_video_gate_when_client_is_supplied(
    tmp_path,
    video_source_item,
) -> None:
    client = StubRuntimeClient(
        search_results=[{"results": []}] * 8,
        database_create_results=[
            {"id": "db_sources"},
            {"id": "db_insights"},
            {"id": "db_ideas"},
            {"id": "db_briefs"},
            {"id": "db_drafts"},
            {"id": "db_events"},
            {"id": "db_scripts"},
            {"id": "db_filming"},
        ],
        page_query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        page_create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    settings = RuntimeSettings(
        notion_api_key="notion-token",
        notion_parent_page_id="34b2a925815780b8bd08d56c7e1293cf",
        anthropic_api_key="anthropic-token",
    )
    n8n_client = StubN8NClient()

    run_configured_live_pipeline(
        settings=settings,
        notion_client=client,
        writer=FakeWriter(),
        collector=StaticSourceCollector([video_source_item]),
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
        knowledge_store=MarkdownKnowledgeStore(tmp_path),
        n8n_client=n8n_client,
    )

    assert len(n8n_client.sent_payloads) == 1
    assert n8n_client.sent_payloads[0]["event"] == "workflow_a_script_ready"


def test_dispatch_video_gate_payloads_sends_video_events(tmp_path, video_source_item) -> None:
    client = StubRuntimeClient(
        search_results=[{"results": []}] * 8,
        database_create_results=[
            {"id": "db_sources"},
            {"id": "db_insights"},
            {"id": "db_ideas"},
            {"id": "db_briefs"},
            {"id": "db_drafts"},
            {"id": "db_events"},
            {"id": "db_scripts"},
            {"id": "db_filming"},
        ],
        page_query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        page_create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    settings = RuntimeSettings(
        notion_api_key="notion-token",
        notion_parent_page_id="34b2a925815780b8bd08d56c7e1293cf",
        anthropic_api_key="anthropic-token",
    )
    results = run_configured_live_pipeline(
        settings=settings,
        notion_client=client,
        writer=FakeWriter(),
        collector=StaticSourceCollector([video_source_item]),
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
        knowledge_store=MarkdownKnowledgeStore(tmp_path),
    )
    n8n_client = StubN8NClient()

    dispatched = dispatch_video_gate_payloads(results, n8n_client)

    assert dispatched == 1
    assert n8n_client.sent_payloads[0]["event"] == "workflow_a_script_ready"
    assert n8n_client.sent_payloads[0]["n8n_envelope"]["route"] == "script_ready"
    assert n8n_client.sent_payloads[0]["telegram_notification"]["channel"] == "telegram"


def test_resolve_anthropic_model_uses_requested_when_available() -> None:
    client = StubModelDiscoveryClient(["claude-sonnet-4-6", "claude-opus-4-7"])

    selected = resolve_anthropic_model(client, "claude-sonnet-4-6")

    assert selected == "claude-sonnet-4-6"


def test_resolve_anthropic_model_falls_back_to_available_sonnet() -> None:
    client = StubModelDiscoveryClient(["claude-opus-4-7", "claude-sonnet-4-6"])

    selected = resolve_anthropic_model(client, "claude-sonnet-4-20250514")

    assert selected == "claude-sonnet-4-6"


def test_resolve_anthropic_model_raises_when_no_supported_writer_model() -> None:
    client = StubModelDiscoveryClient(["claude-haiku-4-5-20251001"])

    with pytest.raises(ValueError, match="No supported Anthropic writer model"):
        resolve_anthropic_model(client, "claude-sonnet-4-20250514")


def test_run_configured_live_pipeline_surfaces_helpful_notion_sharing_error(video_source_item) -> None:
    class DeniedNotionClient:
        def retrieve_page(self, page_id: str) -> dict:
            raise NotionHTTPError(
                status_code=404,
                response_body={
                    "code": "object_not_found",
                    "message": (
                        "Could not find page with ID: page_123. "
                        'Make sure the relevant pages and databases are shared with your integration "Content FABRIC Setup".'
                    ),
                },
                raw_body="notion denied",
            )

    settings = RuntimeSettings(
        notion_api_key="notion-token",
        notion_parent_page_id="34b2a925815780b8bd08d56c7e1293cf",
        anthropic_api_key="anthropic-token",
    )

    with pytest.raises(ValueError, match="share the Notion page with the integration"):
        run_configured_live_pipeline(
            settings=settings,
            notion_client=DeniedNotionClient(),
            writer=FakeWriter(),
            collector=StaticSourceCollector([video_source_item]),
            verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
            submitted_at="2026-04-24T10:00:00Z",
        )
