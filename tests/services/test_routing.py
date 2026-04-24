from content_engine.services.routing import route_signal


def test_route_signal_sends_video_trend_to_workflow_a() -> None:
    signal = {
        "is_video": True,
        "has_trend_hook": True,
        "has_textual_depth": False,
        "relevance_score": 8,
    }

    assert route_signal(signal) == "workflow_a"


def test_route_signal_sends_market_insight_to_workflow_b() -> None:
    signal = {
        "is_video": False,
        "has_trend_hook": False,
        "has_textual_depth": True,
        "relevance_score": 7,
    }

    assert route_signal(signal) == "workflow_b"


def test_route_signal_sends_mixed_high_value_signal_to_both() -> None:
    signal = {
        "is_video": True,
        "has_trend_hook": True,
        "has_textual_depth": True,
        "relevance_score": 9,
    }

    assert route_signal(signal) == "both"


def test_route_signal_drops_low_relevance_signal() -> None:
    signal = {
        "is_video": False,
        "has_trend_hook": False,
        "has_textual_depth": False,
        "relevance_score": 2,
    }

    assert route_signal(signal) == "drop"
