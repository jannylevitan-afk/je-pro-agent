from content_engine.services.ingestion import build_dedupe_key


def test_dedupe_key_uses_external_item_id_when_available() -> None:
    key = build_dedupe_key(
        platform="instagram",
        external_item_id="12345",
        source_url="https://example.com/post/1",
        published_at="2026-04-24T08:00:00Z",
        content_hash="hash_abc",
    )

    assert key == "instagram:12345"


def test_dedupe_key_falls_back_to_hashed_composite() -> None:
    key = build_dedupe_key(
        platform="instagram",
        external_item_id="",
        source_url="https://example.com/post/1",
        published_at="2026-04-24T08:00:00Z",
        content_hash="hash_abc",
    )

    assert key.startswith("instagram:fallback:")


def test_dedupe_key_is_stable_for_identical_input() -> None:
    first = build_dedupe_key(
        platform="telegram",
        external_item_id="",
        source_url="https://t.me/test/1",
        published_at="2026-04-24T08:00:00Z",
        content_hash="hash_xyz",
    )
    second = build_dedupe_key(
        platform="telegram",
        external_item_id="",
        source_url="https://t.me/test/1",
        published_at="2026-04-24T08:00:00Z",
        content_hash="hash_xyz",
    )

    assert first == second
