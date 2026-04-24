from content_engine.models.discovery import DiscoveryCandidate


def test_discovery_candidate_accepts_queue_fields() -> None:
    candidate = DiscoveryCandidate(
        handle="@candidate",
        platform="instagram",
        segment="developer_investor",
        score=7,
        why_relevant="Matches Bali developer keywords and content signals.",
        approved="pending",
        added_to_monitoring=False,
    )

    assert candidate.score == 7
    assert candidate.approved == "pending"
