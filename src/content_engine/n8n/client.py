from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonObject = dict[str, Any]
Transport = Callable[[str, str, dict[str, str], JsonObject], tuple[int, str]]


class N8NWebhookClientError(RuntimeError):
    """Base exception for n8n webhook delivery failures."""


class N8NWebhookHTTPError(N8NWebhookClientError):
    def __init__(
        self,
        status_code: int,
        response_body: JsonObject | None,
        raw_body: str,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.raw_body = raw_body
        super().__init__(f"n8n webhook request failed with status {status_code}")


class N8NWebhookDecodeError(N8NWebhookClientError):
    """Raised when an n8n webhook response is not a JSON object."""


@dataclass(frozen=True, slots=True)
class N8NWebhookClientConfig:
    webhook_url: str
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        webhook_url = self.webhook_url.strip()
        if not webhook_url:
            raise ValueError("webhook_url must not be empty")
        if not webhook_url.startswith(("http://", "https://")):
            raise ValueError("webhook_url must start with http:// or https://")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        object.__setattr__(self, "webhook_url", webhook_url)


class N8NWebhookClient:
    def __init__(
        self,
        config: N8NWebhookClientConfig,
        transport: Transport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or self._default_transport

    def send(self, payload: JsonObject) -> JsonObject:
        status_code, response_text = self._transport(
            "POST",
            self._config.webhook_url,
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            payload,
        )
        if status_code >= 400:
            raise N8NWebhookHTTPError(
                status_code=status_code,
                response_body=_decode_json_or_none(response_text),
                raw_body=response_text,
            )
        return _decode_json_or_raise(response_text)

    def _default_transport(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: JsonObject,
    ) -> tuple[int, str]:
        request = Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self._config.timeout_seconds) as response:
                status = getattr(response, "status", response.getcode())
                body = response.read().decode("utf-8")
                return status, body
        except HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, body
        except URLError as error:
            raise N8NWebhookClientError(f"Network error while calling n8n webhook: {error.reason}") from error


def _decode_json_or_none(text: str) -> JsonObject | None:
    if not text:
        return None
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(decoded, dict):
        return decoded
    return None


def _decode_json_or_raise(text: str) -> JsonObject:
    if not text:
        return {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as error:
        raise N8NWebhookDecodeError("n8n webhook response is not valid JSON") from error
    if not isinstance(decoded, dict):
        raise N8NWebhookDecodeError("n8n webhook response must be a JSON object")
    return decoded
