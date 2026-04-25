from content_engine.models.analytics import ContentPerformanceRecord, DecisionMetrics, FeedbackSignal
from content_engine.models.workflow_b import BriefRecord
from content_engine.notion.payloads import (
    build_brief_properties,
    build_calendar_properties,
    build_content_performance_properties,
    build_draft_properties,
    build_feedback_signal_properties,
    build_orchestration_event_properties,
    build_source_properties,
)
from content_engine.services.approval import build_calendar_item, submit_for_review


def _first_text(property_payload: dict[str, object]) -> str:
    rich_text = property_payload["rich_text"]
    return rich_text[0]["text"]["content"]  # type: ignore[index]


def test_build_draft_properties_contains_linkedin_bilingual_fields(linkedin_draft_record) -> None:
    properties = build_draft_properties(linkedin_draft_record)

    assert _first_text(properties["Draft text RU"]) == "Русская мастер-версия."
    assert _first_text(properties["Draft text EN"]) == "English publish version."
    assert properties["Working language"] == {"select": {"name": "ru"}}
    assert properties["Publish language"] == {"select": {"name": "en"}}
    assert _first_text(properties["Linked brief"]) == "brief_001"
    assert properties["Parent draft"] == {"rich_text": []}
    assert properties["Approval decided at"] == {"date": None}
    assert properties["Writer human review required"] == {"checkbox": False}


def test_build_brief_properties_keeps_reference_sources() -> None:
    brief = BriefRecord(
        brief_id="brief_001",
        title="Investor trust signals",
        audience_portrait="developer_investor",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        funnel_role="authority",
        workflow_stage="brief_ready",
        review_decision="pending",
        source_rigor="expert",
        reference_sources=["https://a.example", "https://b.example", "https://c.example"],
    )

    properties = build_brief_properties(brief)

    assert _first_text(properties["Brief ID"]) == "brief_001"
    assert properties["Linked draft"] == {"rich_text": []}
    assert properties["Review notes"] == {"rich_text": []}
    assert _first_text(properties["Reference sources"]) == "https://a.example\nhttps://b.example\nhttps://c.example"


def test_build_calendar_properties_maps_approved_item(linkedin_draft_record) -> None:
    calendar_item = build_calendar_item(
        linkedin_draft_record,
        approved_at="2026-04-24T12:00:00Z",
    )

    properties = build_calendar_properties(calendar_item)

    assert properties["Platform"] == {"select": {"name": "linkedin"}}
    assert _first_text(properties["Source draft"]) == "dr_001"
    assert _first_text(properties["Final text RU"]) == "Русская мастер-версия."
    assert _first_text(properties["Final text EN"]) == "English publish version."
    assert properties["Approval decided at"] == {"date": {"start": "2026-04-24T12:00:00Z"}}


def test_build_orchestration_event_properties_maps_event_fields(linkedin_draft_record) -> None:
    _, events = submit_for_review(
        draft=linkedin_draft_record,
        submitted_at="2026-04-24T13:00:00Z",
    )
    event = events[0]

    properties = build_orchestration_event_properties(event)

    assert properties["Event name"] == {"select": {"name": "draft_submitted_for_review"}}
    assert properties["Entity type"] == {"select": {"name": "draft"}}
    assert _first_text(properties["Draft ID"]) == "dr_001"
    assert properties["Brief ID"] == {"rich_text": []}
    assert properties["Payload ref"] == {"rich_text": []}


def test_build_source_properties_maps_ingestion_fields(source_item) -> None:
    properties = build_source_properties(source_item)

    assert properties["Platform"] == {"select": {"name": "telegram_post"}}
    assert _first_text(properties["External item ID"]) == "1"
    assert _first_text(properties["Dedupe key"]) == "telegram:1"
    assert properties["Ingestion status"] == {"select": {"name": "collected"}}


def test_build_analytics_properties_map_decision_metrics() -> None:
    record = ContentPerformanceRecord(
        record_id="perf_001",
        linked_content_item_id="cal_dr_001",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        content_theme="boutique_hotels",
        hook_type="market_warning",
        reach=1000,
        impressions=2000,
        saves=50,
        shares=25,
        comments=10,
        profile_visits=60,
        dms_received=5,
        likes=120,
        link_clicks=30,
        inquiry_type="developer",
        attribution_model="time_decay",
        deal_influenced=True,
        performance_tier="top",
    )
    metrics = DecisionMetrics(
        engagement_rate=0.205,
        save_rate=0.05,
        share_rate=0.025,
        dm_rate=0.005,
        ctr=0.015,
    )

    properties = build_content_performance_properties(record, metrics)

    assert _first_text(properties["Linked content item"]) == "cal_dr_001"
    assert properties["Engagement rate"] == {"number": 0.205}
    assert properties["CTR"] == {"number": 0.015}
    assert properties["Attribution model"] == {"select": {"name": "time_decay"}}
    assert properties["Deal influenced"] == {"checkbox": True}


def test_build_feedback_signal_properties() -> None:
    signal = FeedbackSignal(
        signal_id="sig_001",
        signal_scope="platform_lane",
        dimension_value="linkedin_b2b",
        signal_type="boost",
        performance_tier="top",
        score=0.91,
        reason="High-quality inbound developer conversations.",
    )

    properties = build_feedback_signal_properties(signal)

    assert properties["Signal scope"] == {"select": {"name": "platform_lane"}}
    assert _first_text(properties["Dimension value"]) == "linkedin_b2b"
    assert properties["Signal type"] == {"select": {"name": "boost"}}
    assert properties["Score"] == {"number": 0.91}
    assert properties["Applied"] == {"checkbox": False}
