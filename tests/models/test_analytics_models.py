import pytest

from content_engine.models.analytics import ContentPerformanceRecord, FeedbackSignal, TrackingEvent


def test_content_performance_record_keeps_attribution_fields() -> None:
    record = ContentPerformanceRecord(
        record_id="perf_001",
        linked_content_item_id="cal_dr_001",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        content_theme="wellness_architecture",
        hook_type="market_observation",
        reach=1000,
        impressions=2200,
        saves=40,
        shares=25,
        comments=18,
        profile_visits=35,
        dms_received=9,
        likes=70,
        link_clicks=28,
        inquiry_type="developer",
        attribution_model="time_decay",
        deal_influenced=True,
        performance_tier="top",
    )

    assert record.attribution_model == "time_decay"
    assert record.deal_influenced is True


def test_tracking_event_rejects_invalid_name_format() -> None:
    with pytest.raises(ValueError, match="lowercase_with_underscores"):
        TrackingEvent(
            event_name="DraftReviewed",
            entity_id="cal_dr_001",
            occurred_at="2026-04-24T14:00:00Z",
        )


def test_feedback_signal_keeps_scope_and_score() -> None:
    signal = FeedbackSignal(
        signal_id="sig_001",
        signal_scope="content_theme",
        dimension_value="wellness_architecture",
        signal_type="boost",
        performance_tier="top",
        score=0.84,
        reason="High saves and qualified developer replies.",
    )

    assert signal.signal_scope == "content_theme"
    assert signal.score == 0.84

