from content_engine.models.approval import DraftRecord, ReviewAction
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
        draft_text_ru="Русская мастер-версия",
        draft_text_en="English publish version",
        version=1,
        workflow_stage="ai_edited",
        review_decision="pending",
        ai_edited=True,
        seven_point_test_passed=True,
        factual_safety="clean",
        linked_brief_id="brief_001",
    )


def test_submit_for_review_moves_draft_into_review_queue() -> None:
    updated_draft, events = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )

    assert updated_draft.workflow_stage == "awaiting_review"
    assert updated_draft.review_requested_at == "2026-04-24T09:00:00Z"
    assert [event.event_name for event in events] == ["draft_submitted_for_review"]


def test_apply_review_action_approved_builds_calendar_item() -> None:
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

    assert result.updated_draft.workflow_stage == "moved_to_calendar"
    assert result.calendar_item is not None
    assert result.calendar_item.final_text_en == "English publish version"
    assert [event.event_name for event in result.events] == [
        "draft_reviewed",
        "calendar_item_scheduled",
    ]


def test_apply_review_action_rewrite_creates_next_version() -> None:
    submitted_draft, _ = submit_for_review(
        make_linkedin_draft(),
        submitted_at="2026-04-24T09:00:00Z",
    )

    result = apply_review_action(
        submitted_draft,
        ReviewAction(
            decision="needs_rewrite",
            notes="Сделай открытие более живым и менее формальным.",
            decided_at="2026-04-24T09:15:00Z",
        ),
    )

    assert result.updated_draft.workflow_stage == "archived"
    assert result.updated_draft.review_decision == "needs_rewrite"
    assert result.next_draft is not None
    assert result.next_draft.version == 2
    assert result.next_draft.parent_draft_id == "dr_001"
    assert result.next_draft.workflow_stage == "awaiting_review"
    assert result.next_draft.review_decision == "pending"
    assert result.next_draft.draft_text_ru == "Русская мастер-версия"
    assert [event.event_name for event in result.events] == [
        "draft_reviewed",
        "rewrite_requested",
    ]


def test_apply_review_action_re_brief_emits_brief_revision_event() -> None:
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

    assert result.updated_draft.workflow_stage == "archived"
    assert result.updated_draft.review_decision == "re_brief"
    assert result.next_draft is None
    assert result.calendar_item is None
    assert [event.event_name for event in result.events] == [
        "draft_reviewed",
        "brief_revision_requested",
    ]


def test_apply_review_action_deleted_archives_draft() -> None:
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

    assert result.updated_draft.workflow_stage == "archived"
    assert result.updated_draft.archived is True
    assert result.updated_draft.review_decision == "deleted"
    assert [event.event_name for event in result.events] == [
        "draft_reviewed",
        "draft_archived",
    ]
