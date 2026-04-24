from content_engine.notion.bootstrap import ensure_live_pipeline_targets


class StubBootstrapClient:
    def __init__(
        self,
        *,
        search_results: list[dict],
        create_results: list[dict] | None = None,
        retrieve_results: list[dict] | None = None,
        update_results: list[dict] | None = None,
    ) -> None:
        self._search_results = list(search_results)
        self._create_results = list(create_results or [])
        self._retrieve_results = list(retrieve_results or [])
        self._update_results = list(update_results or [])
        self.search_calls: list[str] = []
        self.create_calls: list[tuple[str, str, dict]] = []
        self.retrieve_calls: list[str] = []
        self.update_calls: list[tuple[str, dict]] = []

    def search(self, query: str) -> dict:
        self.search_calls.append(query)
        if not self._search_results:
            raise AssertionError("Unexpected search call")
        return self._search_results.pop(0)

    def create_database(self, parent_page_id: str, title: str, properties: dict) -> dict:
        self.create_calls.append((parent_page_id, title, properties))
        if not self._create_results:
            raise AssertionError("Unexpected create_database call")
        return self._create_results.pop(0)

    def retrieve_database(self, database_id: str) -> dict:
        self.retrieve_calls.append(database_id)
        if not self._retrieve_results:
            raise AssertionError("Unexpected retrieve_database call")
        return self._retrieve_results.pop(0)

    def update_database(self, database_id: str, properties: dict) -> dict:
        self.update_calls.append((database_id, properties))
        if not self._update_results:
            raise AssertionError("Unexpected update_database call")
        return self._update_results.pop(0)


def test_ensure_live_pipeline_targets_creates_missing_databases() -> None:
    client = StubBootstrapClient(
        search_results=[{"results": []}] * 8,
        create_results=[
            {"id": "db_sources"},
            {"id": "db_insights"},
            {"id": "db_ideas"},
            {"id": "db_briefs"},
            {"id": "db_drafts"},
            {"id": "db_events"},
            {"id": "db_scripts"},
            {"id": "db_filming"},
        ],
    )

    targets = ensure_live_pipeline_targets(
        client=client,
        parent_page_id="34b2a925-8157-80b8-bd08-d56c7e1293cf",
    )

    assert targets.sources_database_id == "db_sources"
    assert targets.filming_cards_database_id == "db_filming"
    assert client.create_calls[0][1] == "Content Engine Sources"
    assert client.create_calls[4][2]["Linked brief"] == {"rich_text": {}}


def test_ensure_live_pipeline_targets_updates_existing_schema_when_field_missing() -> None:
    client = StubBootstrapClient(
        search_results=[
            {
                "results": [
                    {
                        "id": "db_sources",
                        "object": "database",
                        "parent": {"type": "page_id", "page_id": "parent_page"},
                        "title": [{"plain_text": "Content Engine Sources"}],
                    }
                ]
            },
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        retrieve_results=[
            {
                "id": "db_sources",
                "properties": {
                    "Title": {"type": "title"},
                    "Platform": {"type": "select"},
                },
            }
        ],
        update_results=[{"id": "db_sources"}],
        create_results=[
            {"id": "db_insights"},
            {"id": "db_ideas"},
            {"id": "db_briefs"},
            {"id": "db_drafts"},
            {"id": "db_events"},
            {"id": "db_scripts"},
            {"id": "db_filming"},
        ],
    )

    targets = ensure_live_pipeline_targets(client=client, parent_page_id="parent_page")

    assert targets.sources_database_id == "db_sources"
    assert client.retrieve_calls == ["db_sources"]
    assert client.update_calls[0][0] == "db_sources"
    assert "Raw text" in client.update_calls[0][1]
