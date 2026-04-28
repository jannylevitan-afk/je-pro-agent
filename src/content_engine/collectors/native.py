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

from content_engine.collectors.apify import fetch_instagram_profile, fetch_tiktok_profile
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
    apify_tiktok_profile_fetcher: ApifyProfileFetcher | None = None
    collected_at: str | None = None

    def collect(self) -> list[SourceItem]:
        return collect_native_source_items(
            targets=self.targets,
            timeout_seconds=self.timeout_seconds,
            fetcher=self.fetcher,
            apify_profile_fetcher=self.apify_profile_fetcher,
            apify_tiktok_profile_fetcher=self.apify_tiktok_profile_fetcher,
            collected_at=self.collected_at,
        )


def collect_native_source_items(
    *,
    targets: list[NativeSourceTarget],
    timeout_seconds: float = 30.0,
    fetcher: Fetcher | None = None,
    apify_profile_fetcher: ApifyProfileFetcher | None = None,
    apify_tiktok_profile_fetcher: ApifyProfileFetcher | None = None,
    collected_at: str | None = None,
) -> list[SourceItem]:
    resolved_fetcher = fetcher or _default_fetcher
    collected_timestamp = collected_at or _utc_now_iso()
    items: list[SourceItem] = []

    for target in targets:
        target_url = resolve_target_url(target)
        if target.platform == "instagram" and _is_instagram_profile_url(target_url):
            profile_payload = (apify_profile_fetcher or _default_apify_profile_fetcher)(target, timeout_seconds)
            items.append(
                _build_instagram_profile_item(
                    target=target,
                    target_url=target_url,
                    profile_payload=profile_payload,
                    collected_at=collected_timestamp,
                )
            )
            continue

        raw_text = resolved_fetcher(target_url, timeout_seconds)
        if target.platform == "telegram":
            target_items = _parse_telegram_channel_page(target, target_url, raw_text, collected_timestamp)
            items.extend(_select_top_performing_items(target_items))
        elif target.platform == "youtube":
            target_items = _parse_youtube_feed(target, target_url, raw_text, collected_timestamp)
            items.extend(_select_top_performing_items(target_items))
        elif target.platform == "tiktok":
            try:
                item = _parse_tiktok_public_page(target, target_url, raw_text, collected_timestamp)
            except ValueError as exc:
                if not _should_use_apify_tiktok_profile_fallback(target, target_url, exc):
                    raise
                profile_payload = (apify_tiktok_profile_fetcher or _default_apify_tiktok_profile_fetcher)(
                    target,
                    timeout_seconds,
                )
                item = _build_tiktok_profile_item(
                    target=target,
                    target_url=target_url,
                    profile_payload=profile_payload,
                    collected_at=collected_timestamp,
                )
            items.append(item)
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
        datetime_match = re.search(r'<time[^>]*datetime="([^"]+)"', block)
        text_match = re.search(
            r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>',
            block,
            flags=re.DOTALL,
        )
        if post_match is None or datetime_match is None:
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
        source_url = f"https://t.me/{post_match.group(1)}"
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
                "source_post_url": source_url,
                "caption_text": transcript_text,
                "post_text": transcript_text,
                "post_title": _first_line(transcript_text),
                "public_metrics": engagement_signals,
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


def _parse_tiktok_public_page(
    target: NativeSourceTarget,
    target_url: str,
    html: str,
    collected_at: str,
) -> SourceItem:
    posts = _extract_tiktok_posts_from_html(html)
    if not posts:
        return _parse_html_meta_page(target, target_url, html, collected_at)

    return _build_tiktok_item_from_posts(
        target=target,
        target_url=target_url,
        posts=posts,
        collected_at=collected_at,
        raw_payload_extra={},
    )


def _build_tiktok_profile_item(
    *,
    target: NativeSourceTarget,
    target_url: str,
    profile_payload: dict[str, Any],
    collected_at: str,
) -> SourceItem:
    posts = [entry for entry in profile_payload.get("latestPosts", []) if isinstance(entry, dict)]
    if not posts:
        raise ValueError("Apify TikTok profile payload did not contain usable posts")

    return _build_tiktok_item_from_posts(
        target=target,
        target_url=target_url,
        posts=posts,
        collected_at=collected_at,
        raw_payload_extra={
            "apify_profile": profile_payload,
        },
    )


def _build_tiktok_item_from_posts(
    *,
    target: NativeSourceTarget,
    target_url: str,
    posts: list[dict[str, Any]],
    collected_at: str,
    raw_payload_extra: dict[str, Any],
) -> SourceItem:
    best_post = _select_top_tiktok_post(posts)
    external_item_id = _tiktok_post_id(best_post)
    caption_text = _tiktok_post_caption(best_post)
    post_title = _tiktok_post_title(best_post)
    image_text = _tiktok_post_image_text(best_post)
    spoken_transcript = _tiktok_post_spoken_transcript(best_post)
    transcript_parts = [
        post_title,
        caption_text,
        image_text,
        spoken_transcript,
    ]
    transcript_text = ". ".join(part for part in transcript_parts if part).strip()
    if not transcript_text:
        raise ValueError("TikTok profile payload did not contain usable text")

    media_urls = _tiktok_post_media_urls(best_post)
    engagement_signals = _tiktok_post_engagement_signals(best_post)
    engagement_score = _engagement_score(engagement_signals)
    source_url = _tiktok_post_url(best_post, target)
    published_at = _normalize_tiktok_timestamp(best_post.get("createTime") or best_post.get("createTimeISO"), collected_at)
    source_type = "tiktok_video"
    route, reason, confidence = _infer_route(source_type, transcript_text, media_urls)
    content_hash = _content_hash(transcript_text, media_urls)

    return SourceItem(
        item_id=f"tiktok_{external_item_id}",
        source_type=source_type,
        source_name=target.source_name or f"@{target.handle.lstrip('@')}",
        source_url=source_url,
        external_item_id=external_item_id,
        collected_at=collected_at,
        published_at=published_at,
        content_hash=content_hash,
        dedupe_key=build_dedupe_key(
            platform="tiktok",
            external_item_id=external_item_id,
            source_url=source_url,
            published_at=published_at,
            content_hash=content_hash,
        ),
        audience_segment=target.audience_segment,
        content_theme=target.content_theme,
        raw_payload={
            "platform": "tiktok",
            "target_url": target_url,
            "source_post_url": source_url,
            "post_title": post_title,
            "video_title": post_title or caption_text,
            "caption_text": caption_text,
            "post_text": transcript_text,
            "image_text": image_text,
            "spoken_transcript": spoken_transcript or caption_text,
            "transcript_source": "caption_or_description",
            "public_metrics": engagement_signals,
            "engagement_score": engagement_score,
            "engagement_rank": 1,
            "scanned_posts_count": len(posts),
            "engagement_selection_reason": _engagement_selection_reason(engagement_score),
            "monitoring_selection": "best_performing_post",
            "selected_post_payload": best_post,
            **raw_payload_extra,
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
    latest_posts = [entry for entry in profile_payload.get("latestPosts", []) if isinstance(entry, dict)]
    best_post = _select_top_instagram_post(latest_posts)
    profile_url = str(profile_payload.get("url") or target_url).strip()
    profile_username = str(profile_payload.get("username") or target.handle.lstrip("@")).strip()
    source_url = _instagram_post_url(best_post) or profile_url
    external_item_id = _instagram_post_id(best_post) or profile_username
    caption_text = _instagram_post_caption(best_post)
    post_title = _instagram_post_title(best_post)
    carousel_text = _instagram_post_carousel_text(best_post)
    image_text = _instagram_post_image_text(best_post)
    transcript_parts = [
        post_title,
        caption_text,
        carousel_text,
        image_text,
    ]
    transcript_text = ". ".join(part for part in transcript_parts if part).strip()
    if not transcript_text:
        raise ValueError("Apify Instagram profile payload did not contain usable text")

    media_urls = _collect_instagram_profile_media_urls([best_post])
    published_at = _normalize_timestamp(str(best_post.get("timestamp", collected_at))) if best_post else collected_at
    source_type = _instagram_post_source_type(best_post)
    route, reason, confidence = _infer_route(source_type, transcript_text, media_urls)
    content_hash = _content_hash(transcript_text, media_urls)
    engagement_signals = _build_instagram_profile_engagement_signals(profile_payload, [best_post] if best_post else [])
    engagement_score = _engagement_score(engagement_signals)

    return SourceItem(
        item_id=f"instagram_{external_item_id}",
        source_type=source_type,
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
            "profile_url": profile_url,
            "profile_username": profile_username,
            "source_post_url": source_url,
            "post_title": post_title,
            "video_title": post_title or caption_text,
            "caption_text": caption_text,
            "post_text": transcript_text,
            "carousel_text": carousel_text,
            "image_text": image_text,
            "spoken_transcript": caption_text,
            "transcript_source": "caption_or_description",
            "public_metrics": engagement_signals,
            "engagement_score": engagement_score,
            "engagement_rank": 1,
            "scanned_posts_count": len(latest_posts),
            "engagement_selection_reason": _engagement_selection_reason(engagement_score),
            "monitoring_selection": "best_performing_post",
            "selected_post_payload": best_post,
            "apify_profile": profile_payload,
        },
        transcript_text=transcript_text,
        media_urls=media_urls,
        engagement_signals=engagement_signals,
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


def _default_apify_tiktok_profile_fetcher(target: NativeSourceTarget, timeout_seconds: float) -> dict[str, Any]:
    return fetch_tiktok_profile(
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


def _should_use_apify_tiktok_profile_fallback(
    target: NativeSourceTarget,
    target_url: str,
    error: ValueError,
) -> bool:
    return (
        target.platform == "tiktok"
        and _is_tiktok_profile_url(target_url)
        and (
            "Could not extract transcript text" in str(error)
            or "TikTok profile payload did not contain usable text" in str(error)
        )
    )


def _is_tiktok_profile_url(url: str) -> bool:
    normalized = url.lower().split("?", 1)[0].rstrip("/")
    return "tiktok.com/@" in normalized and "/video/" not in normalized


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
            for image in images:
                if isinstance(image, str) and image.startswith("https://"):
                    urls.append(image)
                elif isinstance(image, dict):
                    image_url = image.get("url") or image.get("src") or image.get("displayUrl")
                    if isinstance(image_url, str) and image_url.startswith("https://"):
                        urls.append(image_url)
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
            ("sharesCount", "shares"),
            ("savesCount", "saves"),
            ("videoViewCount", "video_views"),
            ("videoPlayCount", "video_views"),
            ("viewsCount", "views"),
            ("viewCount", "views"),
        ):
            value = first.get(source_key)
            if isinstance(value, (int, float)):
                signals[target_key] = int(value)
    return signals


def _select_top_performing_items(items: list[SourceItem]) -> list[SourceItem]:
    if len(items) <= 1:
        return [_with_engagement_selection_metadata(item, rank=1, scanned_count=len(items)) for item in items]

    ranked = sorted(items, key=lambda item: _engagement_score(item.engagement_signals), reverse=True)
    return [_with_engagement_selection_metadata(ranked[0], rank=1, scanned_count=len(items))]


def _with_engagement_selection_metadata(item: SourceItem, *, rank: int, scanned_count: int) -> SourceItem:
    engagement_score = _engagement_score(item.engagement_signals)
    raw_payload = {
        **item.raw_payload,
        "monitoring_selection": "best_performing_post",
        "engagement_rank": rank,
        "scanned_posts_count": scanned_count,
        "engagement_score": engagement_score,
        "engagement_selection_reason": _engagement_selection_reason(engagement_score),
        "public_metrics": item.engagement_signals,
    }
    return item.model_copy(update={"raw_payload": raw_payload})


def _select_top_instagram_post(posts: list[dict[str, Any]]) -> dict[str, Any]:
    if not posts:
        return {}
    return max(posts, key=lambda post: _engagement_score(_instagram_post_engagement_signals(post)))


def _instagram_post_engagement_signals(post: dict[str, Any]) -> dict[str, int]:
    signals: dict[str, int] = {}
    for source_key, target_key in (
        ("likesCount", "likes"),
        ("commentsCount", "comments"),
        ("sharesCount", "shares"),
        ("savesCount", "saves"),
        ("videoViewCount", "video_views"),
        ("videoPlayCount", "video_views"),
        ("viewsCount", "views"),
        ("viewCount", "views"),
    ):
        value = post.get(source_key)
        if isinstance(value, (int, float)):
            signals[target_key] = int(value)
    return signals


def _engagement_score(signals: dict[str, int]) -> float:
    return (
        signals.get("likes", 0)
        + signals.get("comments", 0) * 4
        + signals.get("shares", 0) * 5
        + signals.get("saves", 0) * 5
        + signals.get("views", 0) * 0.02
        + signals.get("video_views", 0) * 0.02
        + signals.get("ratings", 0) * 0.5
    )


def _engagement_selection_reason(score: float) -> str:
    return f"selected as best-performing post by public engagement score={score:.2f}"


def _instagram_post_id(post: dict[str, Any]) -> str:
    for key in ("id", "shortCode", "shortcode", "code"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _instagram_post_url(post: dict[str, Any]) -> str:
    value = post.get("url") or post.get("postUrl") or post.get("link")
    return value.strip() if isinstance(value, str) else ""


def _instagram_post_title(post: dict[str, Any]) -> str:
    for key in ("title", "headline", "videoTitle", "name"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_text_fragment(value)
    return _first_line(_instagram_post_caption(post))


def _instagram_post_caption(post: dict[str, Any]) -> str:
    for key in ("caption", "text", "description", "alt"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_text_fragment(value)
    return ""


def _instagram_post_carousel_text(post: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("carouselText", "carouselTexts", "sidecarText", "sidecarTexts", "imageTexts", "ocrTexts", "ocrText", "imageText"):
        value = post.get(key)
        values.extend(_coerce_text_values(value))
    child_posts = post.get("childPosts")
    if isinstance(child_posts, list):
        for child in child_posts:
            if isinstance(child, dict):
                values.extend(_coerce_text_values(child.get("caption")))
                values.extend(_coerce_text_values(child.get("alt")))
                values.extend(_coerce_text_values(child.get("ocrText")))
    return _join_unique_text(values)


def _instagram_post_image_text(post: dict[str, Any]) -> str:
    values: list[str] = []
    images = post.get("images", [])
    if isinstance(images, list):
        for image in images:
            if isinstance(image, dict):
                values.extend(_coerce_text_values(image.get("alt")))
                values.extend(_coerce_text_values(image.get("caption")))
                values.extend(_coerce_text_values(image.get("ocrText")))
    return _join_unique_text(values)


def _coerce_text_values(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [_normalize_text_fragment(value)]
    if isinstance(value, list):
        return [
            _normalize_text_fragment(str(item))
            for item in value
            if str(item).strip()
        ]
    return []


def _join_unique_text(values: list[str]) -> str:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = _normalize_text_fragment(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return ". ".join(result)


def _instagram_post_source_type(post: dict[str, Any]) -> str:
    post_type = str(post.get("type", "")).lower()
    post_url = _instagram_post_url(post).lower()
    if "video" in post_type or "reel" in post_type or "/reel/" in post_url:
        return "instagram_reel"
    return "instagram_post"


def _extract_tiktok_posts_from_html(html: str) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE):
        attrs = match.group(1)
        script_body = unescape(match.group(2)).strip()
        if not script_body:
            continue
        should_parse = any(
            marker in attrs or marker in script_body
            for marker in ("SIGI_STATE", "__UNIVERSAL_DATA_FOR_REHYDRATION__", "__NEXT_DATA__", "ItemModule")
        )
        if not should_parse:
            continue
        try:
            payload = json.loads(script_body)
        except json.JSONDecodeError:
            continue
        for post in _collect_tiktok_post_candidates(payload):
            post_id = _tiktok_post_id(post)
            if not post_id or post_id in seen:
                continue
            seen.add(post_id)
            posts.append(post)
    return posts


def _collect_tiktok_post_candidates(value: Any) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if _looks_like_tiktok_post(value):
            candidates.append(value)
        for nested in value.values():
            candidates.extend(_collect_tiktok_post_candidates(nested))
    elif isinstance(value, list):
        for nested in value:
            candidates.extend(_collect_tiktok_post_candidates(nested))
    return candidates


def _looks_like_tiktok_post(value: dict[str, Any]) -> bool:
    return bool(
        _tiktok_post_id(value)
        and _tiktok_post_engagement_signals(value)
        and (_tiktok_post_caption(value) or _tiktok_post_media_urls(value) or _tiktok_post_image_text(value))
    )


def _select_top_tiktok_post(posts: list[dict[str, Any]]) -> dict[str, Any]:
    return max(posts, key=lambda post: _engagement_score(_tiktok_post_engagement_signals(post)))


def _tiktok_post_id(post: dict[str, Any]) -> str:
    for key in ("id", "itemId", "awemeId"):
        value = post.get(key)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    video = post.get("video")
    if isinstance(video, dict):
        value = video.get("id")
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def _tiktok_post_url(post: dict[str, Any], target: NativeSourceTarget) -> str:
    for key in ("webVideoUrl", "url", "shareUrl", "videoUrl"):
        value = post.get(key)
        if isinstance(value, str) and value.startswith("https://"):
            return value
    handle = _tiktok_author_handle(post) or target.handle.lstrip("@").strip("/")
    return f"https://www.tiktok.com/@{handle}/video/{_tiktok_post_id(post)}"


def _tiktok_author_handle(post: dict[str, Any]) -> str:
    author = post.get("author")
    if isinstance(author, dict):
        for key in ("uniqueId", "nickname", "name"):
            value = author.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip().lstrip("@")
    for key in ("author", "authorUniqueId", "authorUsername"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lstrip("@")
    return ""


def _tiktok_post_title(post: dict[str, Any]) -> str:
    for key in ("title", "headline", "name"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_text_fragment(value)
    return _first_line(_tiktok_post_caption(post))


def _tiktok_post_caption(post: dict[str, Any]) -> str:
    for key in ("desc", "description", "caption", "text"):
        value = post.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_text_fragment(value)
    return ""


def _tiktok_post_image_text(post: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("imageText", "imageTexts", "ocrText", "ocrTexts", "onScreenText", "overlayText"):
        values.extend(_coerce_text_values(post.get(key)))
    image_post = post.get("imagePost")
    if isinstance(image_post, dict):
        values.extend(_coerce_text_values(image_post.get("title")))
        images = image_post.get("images")
        if isinstance(images, list):
            for image in images:
                if isinstance(image, dict):
                    values.extend(_coerce_text_values(image.get("alt")))
                    values.extend(_coerce_text_values(image.get("caption")))
                    values.extend(_coerce_text_values(image.get("ocrText")))
    return _join_unique_text(values)


def _tiktok_post_spoken_transcript(post: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("transcript", "transcriptText", "videoTranscript", "subtitleText", "speechText"):
        values.extend(_coerce_text_values(post.get(key)))
    subtitle_infos = post.get("subtitleInfos")
    if isinstance(subtitle_infos, list):
        for subtitle in subtitle_infos:
            if isinstance(subtitle, dict):
                values.extend(_coerce_text_values(subtitle.get("text")))
    return _join_unique_text(values)


def _tiktok_post_media_urls(post: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for video_key in ("video", "videoMeta"):
        video = post.get(video_key)
        if not isinstance(video, dict):
            continue
        for key in ("playAddr", "downloadAddr", "cover", "dynamicCover", "originCover"):
            urls.extend(_coerce_url_values(video.get(key)))
        for key in ("coverUrl", "downloadAddr", "playAddr"):
            urls.extend(_coerce_url_values(video.get(key)))
    image_post = post.get("imagePost")
    if isinstance(image_post, dict):
        images = image_post.get("images")
        if isinstance(images, list):
            for image in images:
                urls.extend(_coerce_url_values(image))
    for key in ("videoUrl", "coverUrl", "displayUrl", "thumbnailUrl"):
        urls.extend(_coerce_url_values(post.get(key)))
    return _unique_urls(urls)


def _tiktok_post_engagement_signals(post: dict[str, Any]) -> dict[str, int]:
    signals: dict[str, int] = {}
    for stats in (post.get("stats"), post.get("statsV2"), post):
        if not isinstance(stats, dict):
            continue
        for source_key, target_key in (
            ("playCount", "views"),
            ("viewCount", "views"),
            ("views", "views"),
            ("diggCount", "likes"),
            ("likeCount", "likes"),
            ("likes", "likes"),
            ("commentCount", "comments"),
            ("comments", "comments"),
            ("shareCount", "shares"),
            ("shares", "shares"),
            ("collectCount", "saves"),
            ("saveCount", "saves"),
            ("saves", "saves"),
        ):
            value = stats.get(source_key)
            if isinstance(value, (int, float)):
                signals[target_key] = int(value)
            elif isinstance(value, str) and value.strip():
                signals[target_key] = _parse_metric_value(value)
    return {key: value for key, value in signals.items() if value > 0}


def _normalize_tiktok_timestamp(value: Any, fallback: str) -> str:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, str) and value.strip().isdigit():
        return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, str) and value.strip():
        return _normalize_timestamp(value)
    return fallback


def _coerce_url_values(value: Any) -> list[str]:
    if isinstance(value, str) and value.startswith("https://"):
        return [value]
    if isinstance(value, dict):
        dict_urls: list[str] = []
        for key in ("urlList", "urls", "url", "src"):
            dict_urls.extend(_coerce_url_values(value.get(key)))
        return dict_urls
    if isinstance(value, list):
        list_urls: list[str] = []
        for item in value:
            list_urls.extend(_coerce_url_values(item))
        return list_urls
    return []


def _unique_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def _first_line(text: str) -> str:
    normalized = _normalize_text_fragment(text)
    if not normalized:
        return ""
    return normalized.split(".", 1)[0].strip()


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
