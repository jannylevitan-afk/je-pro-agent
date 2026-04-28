from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ApifyRequest = Callable[[str, bytes, float], list[dict[str, Any]]]

_APIFY_API_BASE = "https://api.apify.com/v2"
_INSTAGRAM_PROFILE_ACTOR_ID = "apify~instagram-profile-scraper"
_TIKTOK_SCRAPER_ACTOR_ID = "clockworks~tiktok-scraper"


def fetch_instagram_profile(
    *,
    handle: str,
    profile_url: str,
    timeout_seconds: float,
    token: str | None = None,
    request: ApifyRequest | None = None,
) -> dict[str, Any]:
    resolved_token = _resolve_token(token)
    if not resolved_token:
        raise ValueError("APIFY_TOKEN is required for Instagram profile fallback")

    payload = {
        "usernames": [_normalize_instagram_input(handle, profile_url)],
        "includeAboutSection": False,
    }
    endpoint = (
        f"{_APIFY_API_BASE}/acts/{_INSTAGRAM_PROFILE_ACTOR_ID}/run-sync-get-dataset-items?"
        + urlencode({"token": resolved_token})
    )
    response = (request or _default_request)(
        endpoint,
        json.dumps(payload).encode("utf-8"),
        timeout_seconds,
    )
    if not response:
        raise ValueError("Apify Instagram profile scraper returned no items")

    first = response[0]
    if not isinstance(first, dict):
        raise ValueError("Apify Instagram profile scraper returned invalid item payload")
    return first


def fetch_tiktok_profile(
    *,
    handle: str,
    profile_url: str,
    timeout_seconds: float,
    token: str | None = None,
    request: ApifyRequest | None = None,
) -> dict[str, Any]:
    resolved_token = _resolve_token(token)
    if not resolved_token:
        raise ValueError("APIFY_TOKEN is required for TikTok profile fallback")

    payload = {
        "profiles": [_normalize_tiktok_input(handle, profile_url)],
        "resultsPerPage": 12,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }
    endpoint = (
        f"{_APIFY_API_BASE}/acts/{_TIKTOK_SCRAPER_ACTOR_ID}/run-sync-get-dataset-items?"
        + urlencode({"token": resolved_token})
    )
    response = (request or _default_request)(
        endpoint,
        json.dumps(payload).encode("utf-8"),
        timeout_seconds,
    )
    profile: dict[str, Any] = {}
    for item in response:
        if not isinstance(item, dict):
            continue
        author_meta = item.get("authorMeta")
        if isinstance(author_meta, dict):
            profile = author_meta
            break
    latest_posts = [
        item
        for item in response
        if isinstance(item, dict) and ("id" in item or "webVideoUrl" in item) and "note" not in item
    ]
    return {
        "profile": profile,
        "latestPosts": latest_posts,
        "raw_items": response,
    }


def _default_request(url: str, body: bytes, timeout_seconds: float) -> list[dict[str, Any]]:
    request = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        decoded = json.loads(response.read().decode("utf-8"))
    if not isinstance(decoded, list):
        raise ValueError("Apify actor response must be a list of dataset items")
    return decoded


def _normalize_instagram_input(handle: str, profile_url: str) -> str:
    normalized_handle = handle.strip().lstrip("@").strip("/")
    if normalized_handle:
        return normalized_handle
    return profile_url.strip()


def _normalize_tiktok_input(handle: str, profile_url: str) -> str:
    normalized_handle = handle.strip().lstrip("@").strip("/")
    if normalized_handle:
        return normalized_handle
    clean_url = profile_url.strip().rstrip("/")
    if "/" in clean_url:
        return clean_url.rsplit("/", 1)[-1].lstrip("@")
    return clean_url.lstrip("@")


def _resolve_token(token: str | None) -> str:
    if token and token.strip():
        return token.strip()

    env_token = os.environ.get("APIFY_TOKEN", "").strip()
    if env_token:
        return env_token

    return _read_env_value(Path(".env.local"), "APIFY_TOKEN")


def _read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""

    prefix = f"{key}="
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or not line.startswith(prefix):
            continue
        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""
