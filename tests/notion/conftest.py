from collections.abc import Sequence

import pytest


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


@pytest.fixture
def stub_notion_client() -> type[StubNotionClient]:
    return StubNotionClient


def first_text(property_payload: dict) -> str:
    rich_text = property_payload["rich_text"]
    return rich_text[0]["text"]["content"]  # type: ignore[index]
