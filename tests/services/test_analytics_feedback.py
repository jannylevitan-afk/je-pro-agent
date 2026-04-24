from content_engine.models.analytics import ContentPerformanceRecord
from content_engine.services.analytics import (
    build_feedback_signal,
    calculate_decision_metrics,
    classify_performance_tier,
    validate_tracking_event_name,
)


def make_performance_record() -> ContentPerformanceRecord:
    return ContentPerformanceRecord(
        record_id="perf_001",
        linked_content_item_id="cal_dr_001",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        content_theme="wellness_architecture",
        hook_type="market_observation",
        reach=1000,
        impressions=2000,
        saves=30,
        shares=20,
        comments=10,
        profile_visits=25,
        dms_received=8,
        likes=40,
        link_clicks=24,
        inquiry_type="developer",
        attribution_model="time_decay",
        deal_influenced=False,
    )


def test_calculate_decision_metrics_returns_expected_rates() -> None:
    metrics = calculate_decision_metrics(make_performance_record())

    assert metrics.engagement_rate == 0.1
    assert metrics.save_rate == 0.03
    assert metrics.dm_rate == 0.008
    assert metrics.ctr == 0.012


def test_classify_performance_tier_marks_top_for_strong_metrics() -> None:
    metrics = calculate_decision_metrics(make_performance_record())

    tier = classify_performance_tier(metrics, deal_influenced=False)

    assert tier == "top"


def test_build_feedback_signal_boosts_top_performing_dimension() -> None:
    record = make_performance_record()
    metrics = calculate_decision_metrics(record)

    signal = build_feedback_signal(
        record,
        metrics,
        signal_scope="content_theme",
        dimension_value=record.content_theme or "unknown",
    )

    assert signal.signal_type == "boost"
    assert signal.performance_tier == "top"


def test_validate_tracking_event_name_enforces_convention() -> None:
    assert validate_tracking_event_name("draft_reviewed") is True
    assert validate_tracking_event_name("DraftReviewed") is False

