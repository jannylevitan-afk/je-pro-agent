import pytest

from content_engine.collectors.http_json import fetch_source_items_from_json_feed


def test_fetch_source_items_from_json_feed_validates_source_items() -> None:
    payload = """
    [
      {
        "item_id": "itm_001",
        "source_type": "telegram_post",
        "source_name": "@clearvisionary",
        "source_url": "https://t.me/clearvisionary/1",
        "external_item_id": "1",
        "collected_at": "2026-04-24T08:00:00Z",
        "published_at": "2026-04-24T07:55:00Z",
        "content_hash": "hash_001",
        "dedupe_key": "telegram:1",
        "audience_segment": "developer_investor",
        "content_theme": "boutique_hotels",
        "raw_payload": {"text": "Boutique hotel ROI beats mass market."},
        "transcript_text": "Boutique hotel ROI beats mass market.",
        "media_urls": [],
        "engagement_signals": {"views": 1200},
        "routing_decision": "workflow_b",
        "routing_reason": "textual depth",
        "routing_confidence": 0.91,
        "processing_state": "collected"
      }
    ]
    """

    items = fetch_source_items_from_json_feed(
        url="https://example.com/feed.json",
        fetcher=lambda _url, _timeout: payload,
    )

    assert len(items) == 1
    assert items[0].item_id == "itm_001"


def test_fetch_source_items_from_json_feed_rejects_non_list_payload() -> None:
    with pytest.raises(ValueError, match="JSON array"):
        fetch_source_items_from_json_feed(
            url="https://example.com/feed.json",
            fetcher=lambda _url, _timeout: '{"unexpected": true}',
        )
