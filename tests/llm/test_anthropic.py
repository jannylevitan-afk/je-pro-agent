from collections.abc import Callable
from typing import Any

import pytest

from content_engine.llm.anthropic import (
    AnthropicClient,
    AnthropicClientConfig,
    AnthropicDecodeError,
    AnthropicHTTPError,
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


def test_create_message_shapes_anthropic_request() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"id":"msg_1","content":[{"type":"text","text":"Hello"}]}')],
    )
    client = AnthropicClient(AnthropicClientConfig(api_key="secret"), transport=transport)

    response = client.create_message(
        system_prompt="You write high-signal social drafts.",
        user_prompt="Draft a LinkedIn post.",
        max_tokens=400,
    )

    assert response["id"] == "msg_1"
    method, path, headers, payload = recorded_calls[0]
    assert method == "POST"
    assert path == "/messages"
    assert headers["x-api-key"] == "secret"
    assert headers["anthropic-version"] == "2023-06-01"
    assert payload == {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 400,
        "system": "You write high-signal social drafts.",
        "messages": [{"role": "user", "content": "Draft a LinkedIn post."}],
    }


def test_generate_text_returns_joined_text_blocks() -> None:
    transport = _make_transport(
        recorded_calls=[],
        responses=[
            (
                200,
                (
                    '{"content":['
                    '{"type":"text","text":"First paragraph."},'
                    '{"type":"tool_use","id":"tool_1","name":"noop","input":{}},'
                    '{"type":"text","text":"Second paragraph."}'
                    ']}'
                ),
            )
        ],
    )
    client = AnthropicClient(AnthropicClientConfig(api_key="secret"), transport=transport)

    text = client.generate_text(
        system_prompt="You are a bilingual content writer.",
        user_prompt="Draft copy.",
        max_tokens=500,
    )

    assert text == "First paragraph.\n\nSecond paragraph."


def test_http_errors_raise_specialized_exception() -> None:
    transport = _make_transport(
        recorded_calls=[],
        responses=[(401, '{"type":"error","error":{"type":"authentication_error"}}')],
    )
    client = AnthropicClient(AnthropicClientConfig(api_key="secret"), transport=transport)

    with pytest.raises(AnthropicHTTPError) as exc_info:
        client.create_message(system_prompt=None, user_prompt="Hello", max_tokens=100)

    assert exc_info.value.status_code == 401
    assert exc_info.value.response_body == {
        "type": "error",
        "error": {"type": "authentication_error"},
    }


def test_generate_text_rejects_non_json_response() -> None:
    transport = _make_transport(
        recorded_calls=[],
        responses=[(200, "not-json")],
    )
    client = AnthropicClient(AnthropicClientConfig(api_key="secret"), transport=transport)

    with pytest.raises(AnthropicDecodeError):
        client.generate_text(system_prompt=None, user_prompt="Hello", max_tokens=100)


def test_list_models_uses_get_models_endpoint() -> None:
    recorded_calls: list[TransportCall] = []
    transport = _make_transport(
        recorded_calls,
        responses=[(200, '{"data":[{"id":"claude-sonnet-4-6"}]}')],
    )
    client = AnthropicClient(AnthropicClientConfig(api_key="secret"), transport=transport)

    response = client.list_models()

    assert response == {"data": [{"id": "claude-sonnet-4-6"}]}
    method, path, headers, payload = recorded_calls[0]
    assert method == "GET"
    assert path == "/models"
    assert headers["x-api-key"] == "secret"
    assert payload is None
