from typing import Any

import pytest

from content_engine.n8n.client import (
    N8NWebhookClient,
    N8NWebhookClientConfig,
    N8NWebhookDecodeError,
    N8NWebhookHTTPError,
)


TransportCall = tuple[str, str, dict[str, str], dict[str, Any]]


def test_webhook_client_posts_json_payload() -> None:
    calls: list[TransportCall] = []

    def transport(
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[int, str]:
        calls.append((method, url, headers, payload))
        return 200, '{"ok":true}'

    client = N8NWebhookClient(
        N8NWebhookClientConfig(webhook_url="https://n8n.example/webhook/video"),
        transport=transport,
    )

    response = client.send({"route": "script_ready", "workflow": "video_pipeline"})

    assert response == {"ok": True}
    method, url, headers, payload = calls[0]
    assert method == "POST"
    assert url == "https://n8n.example/webhook/video"
    assert headers["Content-Type"] == "application/json"
    assert payload["route"] == "script_ready"


def test_webhook_config_rejects_empty_or_non_http_url() -> None:
    with pytest.raises(ValueError, match="webhook_url"):
        N8NWebhookClientConfig(webhook_url="")

    with pytest.raises(ValueError, match="http"):
        N8NWebhookClientConfig(webhook_url="ftp://n8n.example")


def test_webhook_client_raises_for_http_error() -> None:
    def transport(
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[int, str]:
        return 500, '{"error":"boom"}'

    client = N8NWebhookClient(
        N8NWebhookClientConfig(webhook_url="https://n8n.example/webhook/video"),
        transport=transport,
    )

    with pytest.raises(N8NWebhookHTTPError) as exc_info:
        client.send({"route": "script_ready"})

    assert exc_info.value.status_code == 500
    assert exc_info.value.response_body == {"error": "boom"}


def test_webhook_client_accepts_empty_success_response() -> None:
    def transport(
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[int, str]:
        return 204, ""

    client = N8NWebhookClient(
        N8NWebhookClientConfig(webhook_url="https://n8n.example/webhook/video"),
        transport=transport,
    )

    assert client.send({"route": "script_ready"}) == {}


def test_webhook_client_raises_for_non_json_response() -> None:
    def transport(
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[int, str]:
        return 200, "not-json"

    client = N8NWebhookClient(
        N8NWebhookClientConfig(webhook_url="https://n8n.example/webhook/video"),
        transport=transport,
    )

    with pytest.raises(N8NWebhookDecodeError):
        client.send({"route": "script_ready"})
