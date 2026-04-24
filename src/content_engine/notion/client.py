from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonObject = dict[str, Any]
Transport = Callable[[str, str, dict[str, str], JsonObject | None], tuple[int, str]]


class NotionClientError(RuntimeError):
    """Base exception for Notion transport/client failures."""


class NotionHTTPError(NotionClientError):
    def __init__(
        self,
        status_code: int,
        response_body: JsonObject | None,
        raw_body: str,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.raw_body = raw_body
        super().__init__(f"Notion API request failed with status {status_code}")


class NotionDecodeError(NotionClientError):
    """Raised when a Notion response cannot be decoded as JSON object."""


@dataclass(frozen=True, slots=True)
class NotionClientConfig:
    token: str
    base_url: str = "https://api.notion.com/v1"
    notion_version: str = "2022-06-28"
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        token = self.token.strip()
        if not token:
            raise ValueError("token must not be empty")

        base_url = self.base_url.rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")

        if not self.notion_version.strip():
            raise ValueError("notion_version must not be empty")

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        object.__setattr__(self, "token", token)
        object.__setattr__(self, "base_url", base_url)


class NotionClient:
    def __init__(
        self,
        config: NotionClientConfig,
        transport: Transport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or self._default_transport

    def create_database_page(
        self,
        database_id: str,
        properties: JsonObject,
    ) -> JsonObject:
        payload: JsonObject = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        return self._request("POST", "/pages", payload=payload)

    def update_page(
        self,
        page_id: str,
        properties: JsonObject,
    ) -> JsonObject:
        return self._request(
            "PATCH",
            f"/pages/{page_id}",
            payload={"properties": properties},
        )

    def retrieve_page(self, page_id: str) -> JsonObject:
        return self._request("GET", f"/pages/{page_id}")

    def search(self, query: str) -> JsonObject:
        return self._request("POST", "/search", payload={"query": query})

    def create_database(
        self,
        parent_page_id: str,
        title: str,
        properties: JsonObject,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/databases",
            payload={
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title},
                    }
                ],
                "properties": properties,
            },
        )

    def retrieve_database(self, database_id: str) -> JsonObject:
        return self._request("GET", f"/databases/{database_id}")

    def update_database(
        self,
        database_id: str,
        properties: JsonObject,
    ) -> JsonObject:
        return self._request(
            "PATCH",
            f"/databases/{database_id}",
            payload={"properties": properties},
        )

    def query_database(
        self,
        database_id: str,
        query: JsonObject | None = None,
    ) -> JsonObject:
        payload = query if query is not None else {}
        return self._request(
            "POST",
            f"/databases/{database_id}/query",
            payload=payload,
        )

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
            raise NotionHTTPError(
                status_code=status_code,
                response_body=self._decode_json_or_none(response_text),
                raw_body=response_text,
            )
        return self._decode_json_or_raise(response_text)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._config.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Notion-Version": self._config.notion_version,
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
            raise NotionClientError(f"Network error while calling Notion: {error.reason}") from error

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
            raise NotionDecodeError("Notion response is not valid JSON") from error
        if not isinstance(decoded, dict):
            raise NotionDecodeError("Notion response must be a JSON object")
        return decoded
