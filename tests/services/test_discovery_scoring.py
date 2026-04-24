from content_engine.services.discovery import eligible_for_queue, score_candidate


def test_scoring_accumulates_positive_signals() -> None:
    profile = {
        "bio": "Bali real estate developer and investor",
        "geo": "Bali",
        "content_signals": ["ROI", "рендеры"],
        "follower_range": "5K–500K",
        "irrelevant": False,
    }
    criteria = {
        "bio_keywords": ["developer", "investor"],
        "geo": ["Bali", "Dubai"],
        "content_signals": ["ROI", "рендеры"],
        "follower_range": "5K–500K",
    }

    result = score_candidate(profile, criteria)

    assert result.score == 8
    assert eligible_for_queue(result) is True


def test_scoring_penalizes_irrelevant_content() -> None:
    profile = {
        "bio": "Travel creator in Bali",
        "geo": "Bali",
        "content_signals": ["пляж"],
        "follower_range": "5K–500K",
        "irrelevant": True,
    }
    criteria = {
        "bio_keywords": ["developer", "investor"],
        "geo": ["Bali", "Dubai"],
        "content_signals": ["ROI", "рендеры"],
        "follower_range": "5K–500K",
    }

    result = score_candidate(profile, criteria)

    assert result.score == 1
    assert eligible_for_queue(result) is False
