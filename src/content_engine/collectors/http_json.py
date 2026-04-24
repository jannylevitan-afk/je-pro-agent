from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.request import urlopen

from content_engine.models.source_item import SourceItem


Fetcher = Callable[[str, float], str]


def fetch_source_items_from_json_feed(
    url: str,
    timeout_seconds: float = 30.0,
    fetcher: Fetcher | None = None,
) -> list[SourceItem]:
    raw_text = (fetcher or _default_fetcher)(url, timeout_seconds)
    payload = json.loads(raw_text)
    if not isinstance(payload, list):
        raise ValueError("Expected source feed payload to be a JSON array")
    return [SourceItem.model_validate(item) for item in payload]


def _default_fetcher(url: str, timeout_seconds: float) -> str:
    with urlopen(url, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8")
