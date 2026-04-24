from content_engine.models.source_item import SourceItem


def test_source_item_requires_core_identity_fields() -> None:
    item = SourceItem(
        item_id="itm_001",
        source_type="instagram_post",
        source_name="@test_handle",
        source_url="https://example.com/post/1",
        external_item_id="123",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-23T08:00:00Z",
        content_hash="hash_123",
        dedupe_key="instagram:123",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
        raw_payload={"caption": "hello"},
        transcript_text="hello",
        media_urls=["https://example.com/image.jpg"],
        engagement_signals={"likes": 10, "comments": 2, "views": 100},
        routing_decision="workflow_b",
        routing_reason="market observation + textual depth",
        routing_confidence=0.82,
        processing_state="collected",
    )

    assert item.routing_decision == "workflow_b"
    assert item.dedupe_key == "instagram:123"


def test_source_item_rejects_invalid_routing_decision() -> None:
    try:
        SourceItem(
            item_id="itm_001",
            source_type="instagram_post",
            source_name="@test_handle",
            source_url="https://example.com/post/1",
            external_item_id="123",
            collected_at="2026-04-24T08:00:00Z",
            published_at="2026-04-23T08:00:00Z",
            content_hash="hash_123",
            dedupe_key="instagram:123",
            audience_segment="developer_investor",
            content_theme="boutique_hotels",
            raw_payload={"caption": "hello"},
            transcript_text="hello",
            media_urls=["https://example.com/image.jpg"],
            engagement_signals={"likes": 10, "comments": 2, "views": 100},
            routing_decision="wrong_value",
            routing_reason="market observation + textual depth",
            routing_confidence=0.82,
            processing_state="collected",
        )
    except ValueError:
        assert True
    else:
        raise AssertionError("Expected invalid routing decision to fail")
