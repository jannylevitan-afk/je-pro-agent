from hashlib import sha256


def build_dedupe_key(
    platform: str,
    external_item_id: str,
    source_url: str,
    published_at: str,
    content_hash: str,
) -> str:
    if external_item_id:
        return f"{platform}:{external_item_id}"

    composite = f"{source_url}|{published_at}|{content_hash}"
    fallback_hash = sha256(composite.encode("utf-8")).hexdigest()[:16]
    return f"{platform}:fallback:{fallback_hash}"
