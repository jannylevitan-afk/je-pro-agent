from content_engine.models.approval import DraftRecord, ReviewAction
from content_engine.n8n.payloads import (
    build_review_gate_envelope,
    build_telegram_notification_payload,
)
from content_engine.services.approval import apply_review_action, submit_for_review


def make_linkedin_draft() -> DraftRecord:
    return DraftRecord(
        draft_id="dr_001",
        title="Investor trust signals in 2026",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Russian master version",
        draft_text_en="English publish version",
        version=1,
        workflow_stage="ai_edited",
        review_decision="pending",
        ai_edited=True,
        seven_point_test_passed=True,
        factual_safety="clean",
        linked_brief_id="brief_001",
    )


def test_build_review_gate_envelope_for_approved_flow() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="approved",
            decided_at="2026-04-24T09:10:00Z",
        ),
    )

    envelope = build_review_gate_envelope(result)

    assert envelope["route"] == "approved"
    assert envelope["draft"]["workflow_stage"] == "moved_to_calendar"
    assert envelope["calendar_item"]["final_text_en"] == "English publish version"
    assert envelope["next_draft"] is None
    assert envelope["brief_update"] is None


def test_build_review_gate_envelope_for_rewrite_flow() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="needs_rewrite",
            notes="Make opening less formal.",
            rewritten_text_ru="Russian master rewritten",
            rewritten_text_en="English publish rewritten",
            decided_at="2026-04-24T09:15:00Z",
        ),
    )

    envelope = build_review_gate_envelope(result)

    assert envelope["route"] == "needs_rewrite"
    assert envelope["draft"]["archived"] is True
    assert envelope["next_draft"]["version"] == 2
    assert envelope["next_draft"]["parent_draft_id"] == "dr_001"
    assert envelope["calendar_item"] is None


def test_build_review_gate_envelope_for_rebrief_flow() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="re_brief",
            decided_at="2026-04-24T09:20:00Z",
        ),
    )

    envelope = build_review_gate_envelope(result)

    assert envelope["route"] == "re_brief"
    assert envelope["brief_update"]["workflow_stage"] == "revision_needed"
    assert envelope["next_draft"] is None
    assert envelope["calendar_item"] is None


def test_build_review_gate_envelope_for_deleted_flow() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="deleted",
            decided_at="2026-04-24T09:25:00Z",
        ),
    )

    envelope = build_review_gate_envelope(result)

    assert envelope["route"] == "deleted"
    assert envelope["draft"]["archived"] is True
    assert envelope["calendar_item"] is None
    assert envelope["next_draft"] is None
    assert envelope["brief_update"] is None


def test_build_telegram_notification_payload_for_rewrite_flow() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )
    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="needs_rewrite",
            notes="Make opening less formal.",
            rewritten_text_ru="Russian master rewritten",
            rewritten_text_en="English publish rewritten",
            decided_at="2026-04-24T09:15:00Z",
        ),
    )
    envelope = build_review_gate_envelope(result)

    notification = build_telegram_notification_payload(envelope)

    assert notification["channel"] == "telegram"
    assert "version 2" in notification["message"]
    assert notification["route"] == "needs_rewrite"
