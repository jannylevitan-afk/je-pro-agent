from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
from typing import Any, Literal
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from content_engine.collectors.apify import fetch_instagram_profile
from content_engine.models.source_item import RoutingDecision, SourceItem
from content_engine.services.ingestion import build_dedupe_key


Fetcher = Callable[[str, float], str]
NativePlatform = Literal["telegram", "instagram", "linkedin", "youtube", "tiktok", "web"]
ApifyProfileFetcher = Callable[["NativeSourceTarget", float], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class NativeSourceTarget:
    platform: NativePlatform
    handle: str
    audience_segment: str
    content_theme: str
    source_url: str | None = None
    source_name: str | None = None


@dataclass(frozen=True, slots=True)
class NativeSourceCollector:
    targets: list[NativeSourceTarget]
    timeout_seconds: float = 30.0
    fetcher: Fetcher | None = None
    apify_profile_fetcher: ApifyProfileFetcher | None = None
    collected_at: str | None = None

    def collect(self) -> list[SourceItem]:
        return collect_native_source_items(
            targets=self.targets,
            timeout_seconds=self.timeout_seconds,
            fetcher=self.fetcher,
            apify_profile_fetcher=self.apify_profile_fetcher,
            collected_at=self.collected_at,
        )


def collect_native_source_items(
    *,
    targets: list[NativeSourceTarget],
    timeout_seconds: float = 30.0,
    fetcher: Fetcher | None = None,
    apify_profile_fetcher: ApifyProfileFetcher | None = None,
    collected_at: str | None = None,
) -> list[SourceItem]:
    resolved_fetcher = fetcher or _default_fetcher
    collected_timestamp = collected_at or _utc_now_iso()
    items: list[SourceItem] = []

    for target in targets:
        target_url = resolve_target_url(target)
        raw_text = resolved_fetcher(target_url, timeout_seconds)
        if target.platform == "telegram":
            items.extend(_parse_telegram_channel_page(target, target_url, raw_text, collected_timestamp))
        elif target.platform == "youtube":
            items.extend(_parse_youtube_feed(target, target_url, raw_text, collected_timestamp))
        else:
            try:
                item = _parse_html_meta_page(target, target_url, raw_text, collected_timestamp)
            except ValueError as exc:
                if not _should_use_apify_instagram_profile_fallback(target, target_url, exc):
                    raise
                profile_payload = (apify_profile_fetcher or _default_apify_profile_fetcher)(target, timeout_seconds)
                item = _build_instagram_profile_item(
                    target=target,
                    target_url=target_url,
                    profile_payload=profile_payload,
                    collected_at=collected_timestamp,
                )
            items.append(item)
    return items


def resolve_target_url(target: NativeSourceTarget) -> str:
    if target.platform == "web":
        if target.source_url:
            return target.source_url
        normalized = target.handle.strip()
        if normalized.startswith("https://"):
            return normalized
        raise ValueError("Web targets require an https source_url")

    if target.source_url:
        return target.source_url

    normalized = target.handle.strip().lstrip("@").strip("/")
    if target.platform == "telegram":
        return f"https://t.me/s/{normalized}"
    if target.platform == "instagram":
        return f"https://www.instagram.com/{normalized}/"
    if target.platform == "linkedin":
        return f"https://www.linkedin.com/in/{normalized}/"
    if target.platform == "youtube":
        if normalized.startswith("UC"):
            return f"https://www.youtube.com/feeds/videos.xml?channel_id={normalized}"
        return f"https://www.youtube.com/@{normalized}"
    if target.platform == "tiktok":
        if normalized.startswith("@"):
            return f"https://www.tiktok.com/{normalized}"
        return f"https://www.tiktok.com/@{normalized}"
    raise ValueError(f"Unsupported native platform: {target.platform}")


def _parse_telegram_channel_page(
    target: NativeSourceTarget,
    target_url: str,
    html: str,
    collected_at: str,
) -> list[SourceItem]:
    blocks = re.findall(
        r'(<div class="tgme_widget_message_wrap.*?(?=<div class="tgme_widget_message_wrap|\Z))',
        html,
        flags=re.DOTALL,
    )
    items: list[SourceItem] = []
    for block in blocks:
        post_match = re.search(r'data-post="([^"]+/([^"]+))"', block)
        link_match = re.search(r'href="(https://t\.me/[^"]+)"', block)
        datetime_match = re.search(r'<time[^>]*datetime="([^"]+)"', block)
        text_match = re.search(
            r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>',
            block,
            flags=re.DOTALL,
        )
        if post_match is None or link_match is None or datetime_match is None:
            continue

        text_html = text_match.group(1) if text_match is not None else ""
        transcript_text = _clean_html_text(text_html)
        if not transcript_text:
            continue

        external_item_id = post_match.group(2)
        published_at = _normalize_timestamp(datetime_match.group(1))
        media_urls = _extract_media_urls(block)
        views_text = _find_first(
            block,
            r'<span class="tgme_widget_message_views"[^>]*>([^<]+)</span>',
        )
        engagement_signals = {}
        if views_text:
            engagement_signals["views"] = _parse_metric_value(views_text)

        source_type = "telegram_post"
        route, reason, confidence = _infer_route(source_type, transcript_text, media_urls)
        content_hash = _content_hash(transcript_text, media_urls)
        source_url = link_match.group(1)
        item = SourceItem(
            item_id=f"telegram_{external_item_id}",
            source_type=source_type,
            source_name=target.source_name or f"@{target.handle.lstrip('@')}",
            source_url=source_url,
            external_item_id=external_item_id,
            collected_at=collected_at,
            published_at=published_at,
            content_hash=content_hash,
            dedupe_key=build_dedupe_key(
                platform="telegram",
                external_item_id=external_item_id,
                source_url=source_url,
                published_at=published_at,
                content_hash=content_hash,
            ),
            audience_segment=target.audience_segment,
            content_theme=target.content_theme,
            raw_payload={
                "platform": "telegram",
                "target_url": target_url,
                "post_ref": post_match.group(1),
            },
            transcript_text=transcript_text,
            media_urls=media_urls,
            engagement_signals=engagement_signals,
            routing_decision=route,
            routing_reason=reason,
            routing_confidence=confidence,
            processing_state="collected",
        )
        items.append(item)
    return items


def _parse_youtube_feed(
    target: NativeSourceTarget,
    target_url: str,
    xml_text: str,
    collected_at: str,
) -> list[SourceItem]:
    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }
    root = ElementTree.fromstring(xml_text)
    channel_title = root.findtext("atom:title", default="", namespaces=namespaces).strip()
    items: list[SourceItem] = []
    for entry in root.findall("atom:entry", namespaces):
        video_id = entry.findtext("yt:videoId", default="", namespaces=namespaces).strip()
        if not video_id:
            continue
        title = entry.findtext("atom:title", default="", namespaces=namespaces).strip()
        description = entry.findtext(
            "media:group/media:description",
            default="",
            namespaces=namespaces,
        ).strip()
        link = entry.find("atom:link", namespaces)
        raw_href = link.get("href") if link is not None else None
        link_url: str = raw_href if raw_href is not None else f"https://www.youtube.com/watch?v={video_id}"
        published_at = _normalize_timestamp(
            entry.findtext("atom:published", default=collected_at, namespaces=namespaces)
        )
        thumbnail = entry.find("media:group/media:thumbnail", namespaces)
        thumb_url = thumbnail.get("url") if thumbnail is not None else None
        media_urls: list[str] = [thumb_url] if thumb_url else []
        engagement_signals = _extract_youtube_engagement_signals(entry, namespaces)

        transcript_text = ". ".join(part for part in [title, description] if part).strip()
        content_hash = _content_hash(transcript_text, media_urls)
        route, reason, confidence = _infer_route("youtube_video", transcript_text, media_urls)
        item = SourceItem(
            item_id=f"youtube_{video_id}",
            source_type="youtube_video",
            source_name=target.source_name or channel_title or target.handle,
            source_url=link_url,
            external_item_id=video_id,
            collected_at=collected_at,
            published_at=published_at,
            content_hash=content_hash,
            dedupe_key=build_dedupe_key(
                platform="youtube",
                external_item_id=video_id,
                source_url=link_url,
                published_at=published_at,
                content_hash=content_hash,
            ),
            audience_segment=target.audience_segment,
            content_theme=target.content_theme,
            raw_payload={
                "platform": "youtube",
                "target_url": target_url,
                "video_title": title,
                "caption_text": description,
                "spoken_transcript": description,
                "transcript_source": "caption_or_description",
            },
            transcript_text=transcript_text,
            media_urls=media_urls,
            engagement_signals=engagement_signals,
            routing_decision=route,
            routing_reason=reason,
            routing_confidence=confidence,
            processing_state="collected",
        )
        items.append(item)
    return items


def _parse_html_meta_page(
    target: NativeSourceTarget,
    target_url: str,
    html: str,
    collected_at: str,
) -> SourceItem:
    parser = _MetadataParser()
    parser.feed(html)

    source_url = parser.meta.get("og:url") or target_url
    title = parser.meta.get("og:title", "").strip()
    description = parser.meta.get("og:description", "").strip()
    video_title = _extract_json_text(parser.json_ld, ("name", "headline"), fallback=title)
    caption_text = _extract_json_text(parser.json_ld, ("caption", "description"), fallback=description)
    spoken_transcript = _extract_json_text(
        parser.json_ld,
        ("transcript", "transcriptText", "videoTranscript"),
        fallback=caption_text,
    )
    transcript_source = "explicit_transcript" if spoken_transcript != caption_text else "caption_or_description"
    transcript_text = ". ".join(part for part in [video_title, spoken_transcript] if part).strip()
    if not transcript_text:
        raise ValueError(f"Could not extract transcript text from {target.platform} page")

    media_urls = [
        value
        for value in [
            parser.meta.get("og:video"),
            parser.meta.get("og:image"),
        ]
        if value
    ]
    published_at = _normalize_timestamp(
        parser.meta.get("article:published_time")
        or parser.json_ld.get("datePublished")
        or collected_at
    )
    engagement_signals = _extract_interaction_signals(parser.json_ld)
    external_item_id = _extract_external_id_from_url(source_url)
    source_type = _infer_html_source_type(target.platform, source_url, media_urls)
    route, reason, confidence = _infer_route(source_type, transcript_text, media_urls)
    content_hash = _content_hash(transcript_text, media_urls)

    return SourceItem(
        item_id=f"{target.platform}_{external_item_id}",
        source_type=source_type,
        source_name=target.source_name or target.handle,
        source_url=source_url,
        external_item_id=external_item_id,
        collected_at=collected_at,
        published_at=published_at,
        content_hash=content_hash,
        dedupe_key=build_dedupe_key(
            platform=target.platform,
            external_item_id=external_item_id,
            source_url=source_url,
            published_at=published_at,
            content_hash=content_hash,
        ),
        audience_segment=target.audience_segment,
        content_theme=target.content_theme,
        raw_payload={
            "platform": target.platform,
            "target_url": target_url,
            "video_title": video_title,
            "caption_text": caption_text,
            "spoken_transcript": spoken_transcript,
            "transcript_source": transcript_source,
            "meta": parser.meta,
            "json_ld": parser.json_ld,
        },
        transcript_text=transcript_text,
        media_urls=media_urls,
        engagement_signals=engagement_signals,
        routing_decision=route,
        routing_reason=reason,
        routing_confidence=confidence,
        processing_state="collected",
    )


def _build_instagram_profile_item(
    *,
    target: NativeSourceTarget,
    target_url: str,
    profile_payload: dict[str, Any],
    collected_at: str,
) -> SourceItem:
    source_url = str(profile_payload.get("url") or target_url).strip()
    external_item_id = str(profile_payload.get("username") or target.handle.lstrip("@")).strip()

    latest_posts = [entry for entry in profile_payload.get("latestPosts", []) if isinstance(entry, dict)]
    transcript_parts = [
        _normalize_text_fragment(str(profile_payload.get("fullName", ""))),
        _normalize_text_fragment(str(profile_payload.get("biography", ""))),
        *[
            _normalize_text_fragment(str(post.get("caption", "")))
            for post in latest_posts[:3]
            if str(post.get("caption", "")).strip()
        ],
    ]
    transcript_text = ". ".join(part for part in transcript_parts if part).strip()
    if not transcript_text:
        raise ValueError("Apify Instagram profile payload did not contain usable text")

    media_urls = _collect_instagram_profile_media_urls(latest_posts[:3])
    published_at = _normalize_timestamp(str(latest_posts[0].get("timestamp", collected_at))) if latest_posts else collected_at
    route, reason, confidence = _infer_route("instagram_profile", transcript_text, media_urls)
    content_hash = _content_hash(transcript_text, media_urls)

    return SourceItem(
        item_id=f"instagram_{external_item_id}",
        source_type="instagram_profile",
        source_name=target.source_name or external_item_id,
        source_url=source_url,
        external_item_id=external_item_id,
        collected_at=collected_at,
        published_at=published_at,
        content_hash=content_hash,
        dedupe_key=build_dedupe_key(
            platform="instagram",
            external_item_id=external_item_id,
            source_url=source_url,
            published_at=published_at,
            content_hash=content_hash,
        ),
        audience_segment=target.audience_segment,
        content_theme=target.content_theme,
        raw_payload={
            "platform": "instagram",
            "target_url": target_url,
            "video_title": _normalize_text_fragment(str(latest_posts[0].get("caption", ""))) if latest_posts else "",
            "caption_text": _normalize_text_fragment(str(latest_posts[0].get("caption", ""))) if latest_posts else "",
            "spoken_transcript": _normalize_text_fragment(str(latest_posts[0].get("caption", ""))) if latest_posts else "",
            "transcript_source": "caption_or_description",
            "apify_profile": profile_payload,
        },
        transcript_text=transcript_text,
        media_urls=media_urls,
        engagement_signals=_build_instagram_profile_engagement_signals(profile_payload, latest_posts),
        routing_decision=route,
        routing_reason=reason,
        routing_confidence=confidence,
        processing_state="collected",
    )


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.json_ld: dict[str, Any] = {}
        self._in_json_ld = False
        self._json_ld_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "meta":
            key = attr_map.get("property") or attr_map.get("name")
            value = attr_map.get("content", "")
            if key:
                self.meta[key] = value
        elif tag == "script" and attr_map.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_ld_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            raw_json = "".join(self._json_ld_chunks).strip()
            if not raw_json:
                return
            try:
                decoded = json.loads(raw_json)
            except json.JSONDecodeError:
                return
            if isinstance(decoded, dict):
                self.json_ld = decoded
            elif isinstance(decoded, list):
                merged = next((item for item in decoded if isinstance(item, dict)), None)
                if isinstance(merged, dict):
                    self.json_ld = merged


def _default_apify_profile_fetcher(target: NativeSourceTarget, timeout_seconds: float) -> dict[str, Any]:
    return fetch_instagram_profile(
        handle=target.handle,
        profile_url=resolve_target_url(target),
        timeout_seconds=timeout_seconds,
    )


def _default_fetcher(url: str, timeout_seconds: float) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8")


def _should_use_apify_instagram_profile_fallback(
    target: NativeSourceTarget,
    target_url: str,
    error: ValueError,
) -> bool:
    return (
        target.platform == "instagram"
        and _is_instagram_profile_url(target_url)
        and "Could not extract transcript text" in str(error)
    )


def _is_instagram_profile_url(url: str) -> bool:
    normalized = url.lower()
    return "instagram.com" in normalized and all(
        token not in normalized
        for token in ("/reel/", "/p/", "/tv/", "/stories/", "/video/")
    )


def _normalize_text_fragment(value: str) -> str:
    return " ".join(value.split()).strip()


def _collect_instagram_profile_media_urls(posts: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for post in posts:
        for key in ("videoUrl", "displayUrl", "url"):
            value = post.get(key)
            if isinstance(value, str) and value.startswith("https://"):
                urls.append(value)
        images = post.get("images", [])
        if isinstance(images, list):
            urls.extend(image for image in images if isinstance(image, str) and image.startswith("https://"))
    return urls


def _build_instagram_profile_engagement_signals(
    profile_payload: dict[str, Any],
    latest_posts: list[dict[str, Any]],
) -> dict[str, int]:
    signals: dict[str, int] = {}
    for source_key, target_key in (
        ("followersCount", "followers"),
        ("followsCount", "following"),
        ("postsCount", "posts"),
    ):
        value = profile_payload.get(source_key)
        if isinstance(value, (int, float)):
            signals[target_key] = int(value)

    if latest_posts:
        first = latest_posts[0]
        for source_key, target_key in (
            ("likesCount", "likes"),
            ("commentsCount", "comments"),
            ("videoViewCount", "video_views"),
        ):
            value = first.get(source_key)
            if isinstance(value, (int, float)):
                signals[target_key] = int(value)
    return signals


def _clean_html_text(text_html: str) -> str:
    with_breaks = re.sub(r"<br\s*/?>", "\n", text_html, flags=re.IGNORECASE)
    without_tags = re.sub(r"<[^>]+>", " ", with_breaks)
    normalized = unescape(without_tags)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n\s+", "\n", normalized)
    return normalized.strip()


def _extract_media_urls(block_or_html: str) -> list[str]:
    urls = re.findall(r'(?:src|href)="(https://[^"]+)"', block_or_html)
    return [
        url
        for url in urls
        if any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".mp4"))
    ]


def _parse_metric_value(raw_value: str) -> int:
    normalized = raw_value.strip().upper().replace(",", ".")
    multiplier = 1
    if normalized.endswith("K"):
        multiplier = 1000
        normalized = normalized[:-1]
    elif normalized.endswith("M"):
        multiplier = 1_000_000
        normalized = normalized[:-1]

    try:
        return int(float(normalized) * multiplier)
    except ValueError:
        return 0


def _content_hash(transcript_text: str, media_urls: list[str]) -> str:
    payload = f"{transcript_text}|{'|'.join(media_urls)}"
    return sha256(payload.encode("utf-8")).hexdigest()[:16]


def _extract_youtube_engagement_signals(
    entry: ElementTree.Element,
    namespaces: dict[str, str],
) -> dict[str, int]:
    signals: dict[str, int] = {}
    statistics = entry.find("media:group/media:community/media:statistics", namespaces)
    if statistics is not None:
        views = statistics.get("views")
        if views is not None:
            signals["views"] = _parse_metric_value(views)
    star_rating = entry.find("media:group/media:community/media:starRating", namespaces)
    if star_rating is not None:
        count = star_rating.get("count")
        if count is not None:
            signals["ratings"] = _parse_metric_value(count)
    return signals


def _infer_route(source_type: str, transcript_text: str, media_urls: list[str]) -> tuple[RoutingDecision, str, float]:
    words = len(transcript_text.split())
    has_video_signal = bool(media_urls) or any(token in source_type for token in ("video", "reel", "tiktok"))
    if has_video_signal and words >= 8:
        return "both", "video signal with textual depth", 0.92
    if has_video_signal:
        return "workflow_a", "video-native source", 0.88
    if words >= 8:
        return "workflow_b", "textual depth from native collector", 0.84
    return "drop", "insufficient signal from native collector", 0.55


def _normalize_timestamp(value: str) -> str:
    normalized = value.strip()
    if normalized.endswith("+00:00"):
        return normalized.replace("+00:00", "Z")
    return normalized


def _extract_external_id_from_url(url: str) -> str:
    clean = url.split("?", 1)[0].rstrip("/")
    parts = [part for part in clean.split("/") if part]
    if not parts:
        return sha256(url.encode("utf-8")).hexdigest()[:12]
    if parts[-2:] and parts[-2] in {"reel", "video", "posts", "post"}:
        return parts[-1]
    return parts[-1]


def _infer_html_source_type(platform: NativePlatform, source_url: str, media_urls: list[str]) -> str:
    normalized_url = source_url.lower()
    if platform == "instagram":
        if "/reel/" in normalized_url:
            return "instagram_reel"
        return "instagram_post"
    if platform == "linkedin":
        if media_urls and any(url.lower().endswith(".mp4") for url in media_urls):
            return "linkedin_video"
        return "linkedin_post"
    if platform == "tiktok":
        return "tiktok_video"
    if platform == "web":
        if any(token in normalized_url for token in ("report", "reports", "outlook", "insight")):
            return "web_report"
        if any(token in normalized_url for token in ("news", "article", "blog")):
            return "web_article"
        return "web_page"
    return f"{platform}_post"


def _extract_json_text(json_ld: dict[str, Any], keys: tuple[str, ...], *, fallback: str = "") -> str:
    for key in keys:
        value = json_ld.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_text_fragment(value)
    return _normalize_text_fragment(fallback)


def _extract_interaction_signals(json_ld: dict[str, Any]) -> dict[str, int]:
    interaction = json_ld.get("interactionStatistic")
    signals: dict[str, int] = {}
    if isinstance(interaction, list):
        for item in interaction:
            if isinstance(item, dict) and "userInteractionCount" in item:
                metric_name = _interaction_metric_name(item)
                signals[metric_name] = _parse_metric_value(str(item["userInteractionCount"]))
        return signals
    if isinstance(interaction, dict) and "userInteractionCount" in interaction:
        return {
            _interaction_metric_name(interaction): _parse_metric_value(str(interaction["userInteractionCount"]))
        }
    return {}


def _interaction_metric_name(item: dict[str, Any]) -> str:
    interaction_type = str(item.get("interactionType", "")).lower()
    if "watchaction" in interaction_type or "viewaction" in interaction_type:
        return "views"
    if "likeaction" in interaction_type:
        return "likes"
    if "commentaction" in interaction_type:
        return "comments"
    if "shareaction" in interaction_type:
        return "shares"
    return "interactions"


def _find_first(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.DOTALL)
    if match is None:
        return None
    return match.group(1).strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
