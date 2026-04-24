from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonObject = dict[str, Any]
Transport = Callable[[str, str, dict[str, str], JsonObject | None], tuple[int, str]]


class AnthropicClientError(RuntimeError):
    """Base exception for Anthropic transport/client failures."""


class AnthropicHTTPError(AnthropicClientError):
    def __init__(
        self,
        status_code: int,
        response_body: JsonObject | None,
        raw_body: str,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.raw_body = raw_body
        super().__init__(f"Anthropic API request failed with status {status_code}")


class AnthropicDecodeError(AnthropicClientError):
    """Raised when an Anthropic response cannot be decoded as JSON object."""


@dataclass(frozen=True, slots=True)
class AnthropicClientConfig:
    api_key: str
    base_url: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"
    model: str = "claude-sonnet-4-20250514"
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        api_key = self.api_key.strip()
        if not api_key:
            raise ValueError("api_key must not be empty")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if not self.anthropic_version.strip():
            raise ValueError("anthropic_version must not be empty")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
        object.__setattr__(self, "anthropic_version", self.anthropic_version.strip())
        object.__setattr__(self, "model", self.model.strip())


class AnthropicClient:
    def __init__(
        self,
        config: AnthropicClientConfig,
        transport: Transport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or self._default_transport

    def create_message(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        max_tokens: int,
        model: str | None = None,
        temperature: float | None = None,
    ) -> JsonObject:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero")

        payload: JsonObject = {
            "model": model or self._config.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        if temperature is not None:
            payload["temperature"] = temperature

        return self._request("POST", "/messages", payload=payload)

    def list_models(self) -> JsonObject:
        return self._request("GET", "/models")

    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        max_tokens: int,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        response = self.create_message(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            model=model,
            temperature=temperature,
        )
        blocks = response.get("content")
        if not isinstance(blocks, list):
            raise AnthropicDecodeError("Anthropic response content must be a list")

        text_blocks = [
            block["text"]
            for block in blocks
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
            and block["text"].strip()
        ]
        if not text_blocks:
            raise AnthropicDecodeError("Anthropic response did not include text content")
        return "\n\n".join(text_blocks)

    def _request(
        self,
        method: str,
        path: str,
        payload: JsonObject | None = None,
    ) -> JsonObject:
        status_code, response_text = self._transport(
            method,
            path,
            self._headers(),
            payload,
        )
        if status_code >= 400:
            raise AnthropicHTTPError(
                status_code=status_code,
                response_body=self._decode_json_or_none(response_text),
                raw_body=response_text,
            )
        return self._decode_json_or_raise(response_text)

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._config.api_key,
            "anthropic-version": self._config.anthropic_version,
            "content-type": "application/json",
            "accept": "application/json",
        }

    def _default_transport(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        payload: JsonObject | None,
    ) -> tuple[int, str]:
        request_payload = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url=f"{self._config.base_url}{path}",
            data=request_payload,
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
            raise AnthropicClientError(
                f"Network error while calling Anthropic: {error.reason}"
            ) from error

    @staticmethod
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

    @staticmethod
    def _decode_json_or_raise(text: str) -> JsonObject:
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError as error:
            raise AnthropicDecodeError("Anthropic response is not valid JSON") from error
        if not isinstance(decoded, dict):
            raise AnthropicDecodeError("Anthropic response must be a JSON object")
        return decoded
