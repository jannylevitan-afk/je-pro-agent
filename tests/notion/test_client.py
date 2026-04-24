from collections.abc import Callable
from typing import Any

import pytest

from content_engine.notion.client import (
    NotionClient,
    NotionClientConfig,
    NotionDecodeError,
    NotionHTTPError,
)


TransportResponse = tuple[int, str]
TransportCall = tuple[str, str, dict[str, str], dict[str, Any] | None]
Transport = Callable[
    [str, str, dict[str, str], dict[str, Any] | None],
    TransportResponse,
]


def _make_transport(
    recorded_calls: list[TransportCall],
    responses: list[TransportResponse],
) -> Transport:
    def _transport(
        method: str,
        path: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None,
    ) -> TransportResponse:
        recorded_calls.append((method, path, headers, payload))
        return responses.pop(0)

    return _transport


def test_create_database_page_shapes_request() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"id":"page_1"}')],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    result = client.create_database_page(
        database_id="db_123",
        properties={"Title": {"title": []}},
    )

    assert result == {"id": "page_1"}
    method, path, headers, payload = recorded_calls[0]
    assert method == "POST"
    assert path == "/pages"
    assert headers["Authorization"] == "Bearer secret"
    assert headers["Notion-Version"] == "2022-06-28"
    assert payload == {
        "parent": {"database_id": "db_123"},
        "properties": {"Title": {"title": []}},
    }


def test_query_database_with_default_payload() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"results":[]}')],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    result = client.query_database(database_id="db_123")

    assert result == {"results": []}
    method, path, _, payload = recorded_calls[0]
    assert method == "POST"
    assert path == "/databases/db_123/query"
    assert payload == {}


def test_update_page_shapes_request() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"id":"page_1"}')],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    result = client.update_page(
        page_id="page_1",
        properties={"Status": {"select": {"name": "Done"}}},
    )

    assert result == {"id": "page_1"}
    method, path, _, payload = recorded_calls[0]
    assert method == "PATCH"
    assert path == "/pages/page_1"
    assert payload == {"properties": {"Status": {"select": {"name": "Done"}}}}


def test_retrieve_page_uses_get_without_payload() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"id":"page_1","object":"page"}')],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    result = client.retrieve_page(page_id="page_1")

    assert result["object"] == "page"
    method, path, _, payload = recorded_calls[0]
    assert method == "GET"
    assert path == "/pages/page_1"
    assert payload is None


def test_http_error_maps_status_and_body() -> None:
    transport = _make_transport(
        recorded_calls=[],
        responses=[(400, '{"code":"validation_error","message":"bad request"}')],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    with pytest.raises(NotionHTTPError) as exc_info:
        client.retrieve_page(page_id="page_1")

    assert exc_info.value.status_code == 400
    assert exc_info.value.response_body == {"code": "validation_error", "message": "bad request"}


def test_decode_error_raises_specialized_exception() -> None:
    transport = _make_transport(
        recorded_calls=[],
        responses=[(200, "not-json")],
    )
    client = NotionClient(NotionClientConfig(token="secret"), transport=transport)

    with pytest.raises(NotionDecodeError):
        client.retrieve_page(page_id="page_1")


def test_config_rejects_empty_token() -> None:
    with pytest.raises(ValueError, match="token must not be empty"):
        NotionClientConfig(token=" ")
