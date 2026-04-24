import pytest

from content_engine.models.approval import CalendarItem, DraftRecord, OrchestrationEvent, ReviewAction
from content_engine.models.workflow_b import BriefRecord


def test_draft_record_keeps_review_and_bilingual_metadata() -> None:
    draft = DraftRecord(
        draft_id="dr_001",
        title="Why cheap villas are the most expensive mistake",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Русская рабочая версия",
        draft_text_en="English publish version",
        version=1,
        workflow_stage="draft_generated",
        review_decision="pending",
        ai_edited=True,
        seven_point_test_passed=True,
        factual_safety="clean",
        linked_brief_id="brief_001",
    )

    assert draft.version == 1
    assert draft.publish_language == "en"
    assert draft.linked_brief_id == "brief_001"


def test_review_action_requires_notes_for_needs_rewrite() -> None:
    with pytest.raises(ValueError, match="needs_rewrite"):
        ReviewAction(
            decision="needs_rewrite",
            decided_at="2026-04-24T09:00:00Z",
        )


def test_review_action_requires_rewritten_text_for_needs_rewrite() -> None:
    with pytest.raises(ValueError, match="rewritten_text_ru"):
        ReviewAction(
            decision="needs_rewrite",
            notes="Needs a rewrite.",
            decided_at="2026-04-24T09:00:00Z",
        )


def test_calendar_item_requires_english_publish_version_for_linkedin() -> None:
    with pytest.raises(ValueError, match="English"):
        CalendarItem(
            calendar_item_id="cal_001",
            source_draft_id="dr_001",
            title="Investor trust signals in 2026",
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            working_language="ru",
            publish_language="en",
            audience_portrait="developer_investor",
            voice_register_used="register_3",
            funnel_role="authority",
            final_text_ru="Русская мастер-версия",
            final_text_en=None,
            approval_status="approved",
            approval_decided_at="2026-04-24T09:00:00Z",
        )


def test_orchestration_event_keeps_stable_event_name() -> None:
    event = OrchestrationEvent(
        event_name="calendar_item_scheduled",
        entity_type="calendar_item",
        entity_id="cal_001",
        status="completed",
        triggered_at="2026-04-24T09:00:00Z",
        draft_id="dr_001",
    )

    assert event.event_name == "calendar_item_scheduled"


def test_brief_record_tracks_revision_needed_state() -> None:
    brief = BriefRecord(
        brief_id="brief_001",
        title="Wellness architecture as investor signal",
        audience_portrait="developer_investor",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        funnel_role="authority",
        workflow_stage="revision_needed",
        review_decision="pending",
        linked_draft_id="dr_001",
    )

    assert brief.workflow_stage == "revision_needed"
