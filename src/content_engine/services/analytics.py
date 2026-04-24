import re

from content_engine.models.analytics import (
    ContentPerformanceRecord,
    DecisionMetrics,
    FeedbackSignal,
    PerformanceTier,
    SignalScope,
    SignalType,
)


def calculate_decision_metrics(record: ContentPerformanceRecord) -> DecisionMetrics:
    engagement_total = record.likes + record.comments + record.shares + record.saves
    reach = record.reach or 1
    impressions = record.impressions or 1
    return DecisionMetrics(
        engagement_rate=engagement_total / reach,
        save_rate=record.saves / reach,
        share_rate=record.shares / reach,
        dm_rate=record.dms_received / reach,
        ctr=record.link_clicks / impressions,
    )


def classify_performance_tier(
    metrics: DecisionMetrics,
    deal_influenced: bool,
) -> PerformanceTier:
    if deal_influenced or metrics.engagement_rate >= 0.08 or metrics.dm_rate >= 0.01:
        return "top"
    if metrics.engagement_rate >= 0.04 or metrics.save_rate >= 0.02 or metrics.share_rate >= 0.015:
        return "average"
    return "weak"


def build_feedback_signal(
    record: ContentPerformanceRecord,
    metrics: DecisionMetrics,
    signal_scope: SignalScope,
    dimension_value: str,
) -> FeedbackSignal:
    performance_tier = classify_performance_tier(
        metrics,
        deal_influenced=record.deal_influenced,
    )
    _tier_to_signal: dict[PerformanceTier, SignalType] = {
        "top": "boost",
        "average": "monitor",
        "weak": "suppress",
    }
    signal_type: SignalType = _tier_to_signal[performance_tier]
    score = min(metrics.engagement_rate + (metrics.dm_rate * 10), 1.0)
    return FeedbackSignal(
        signal_id=f"sig_{record.record_id}_{signal_scope}",
        signal_scope=signal_scope,
        dimension_value=dimension_value,
        signal_type=signal_type,
        performance_tier=performance_tier,
        score=round(score, 3),
        reason=_build_reason(record, metrics, performance_tier),
    )


def validate_tracking_event_name(event_name: str) -> bool:
    return re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", event_name) is not None


def _build_reason(
    record: ContentPerformanceRecord,
    metrics: DecisionMetrics,
    performance_tier: PerformanceTier,
) -> str:
    if performance_tier == "top":
        return (
            f"High engagement ({metrics.engagement_rate:.3f}) "
            f"and qualified {record.inquiry_type} interest."
        )
    if performance_tier == "average":
        return "Stable signal worth monitoring against the historical baseline."
    return "Low decision value compared with current engagement and conversion thresholds."
