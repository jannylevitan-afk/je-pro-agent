from content_engine.models.approval import (
    ApprovalResult,
    CalendarItem,
    DraftRecord,
    EventEntityType,
    EventName,
    OrchestrationEvent,
    ReviewAction,
)
from content_engine.models.workflow_b import BriefRecord


def submit_for_review(
    draft: DraftRecord,
    submitted_at: str,
) -> tuple[DraftRecord, list[OrchestrationEvent]]:
    if draft.factual_safety == "blocked":
        raise ValueError("Blocked drafts cannot enter review")

    updated_draft = draft.model_copy(
        update={
            "workflow_stage": "awaiting_review",
            "review_decision": "pending",
            "review_requested_at": submitted_at,
            "archived": False,
        }
    )
    events = [
        _build_event(
            event_name="draft_submitted_for_review",
            entity_type="draft",
            entity_id=updated_draft.draft_id,
            triggered_at=submitted_at,
            draft_id=updated_draft.draft_id,
        )
    ]
    return updated_draft, events


def apply_review_action(
    draft: DraftRecord,
    action: ReviewAction,
) -> ApprovalResult:
    reviewed_draft = draft.model_copy(
        update={
            "review_decision": action.decision,
            "review_notes": action.notes,
            "approval_decided_at": action.decided_at,
        }
    )
    events = [
        _build_event(
            event_name="draft_reviewed",
            entity_type="draft",
            entity_id=reviewed_draft.draft_id,
            triggered_at=action.decided_at,
            draft_id=reviewed_draft.draft_id,
        )
    ]

    if action.decision == "approved":
        calendar_item = build_calendar_item(reviewed_draft, approved_at=action.decided_at)
        updated_draft = reviewed_draft.model_copy(
            update={
                "workflow_stage": "moved_to_calendar",
                "linked_calendar_id": calendar_item.calendar_item_id,
            }
        )
        events.append(
            _build_event(
                event_name="calendar_item_scheduled",
                entity_type="calendar_item",
                entity_id=calendar_item.calendar_item_id,
                triggered_at=action.decided_at,
                draft_id=updated_draft.draft_id,
                calendar_item_id=calendar_item.calendar_item_id,
            )
        )
        return ApprovalResult(
            updated_draft=updated_draft,
            calendar_item=calendar_item,
            events=events,
        )

    if action.decision == "needs_rewrite":
        archived_draft = reviewed_draft.model_copy(
            update={
                "workflow_stage": "archived",
                "archived": True,
            }
        )
        if draft.platform_lane == "linkedin_b2b" and not action.rewritten_text_en:
            raise ValueError("LinkedIn rewrite requires rewritten_text_en")
        next_draft = archived_draft.model_copy(
            update={
                "draft_id": _next_draft_id(archived_draft),
                "version": archived_draft.version + 1,
                "parent_draft_id": draft.draft_id,
                "workflow_stage": "awaiting_review",
                "review_decision": "pending",
                "review_notes": None,
                "review_requested_at": action.decided_at,
                "approval_decided_at": None,
                "linked_calendar_id": None,
                "archived": False,
                "draft_text_ru": action.rewritten_text_ru,
                "draft_text_en": action.rewritten_text_en
                if action.rewritten_text_en is not None
                else archived_draft.draft_text_en,
            }
        )
        events.append(
            _build_event(
                event_name="rewrite_requested",
                entity_type="draft",
                entity_id=next_draft.draft_id,
                triggered_at=action.decided_at,
                draft_id=next_draft.draft_id,
                payload_ref=draft.draft_id,
            )
        )
        return ApprovalResult(
            updated_draft=archived_draft,
            next_draft=next_draft,
            events=events,
        )

    if action.decision == "re_brief":
        brief_update = BriefRecord(
            brief_id=draft.linked_brief_id or f"brief_{draft.draft_id}",
            title=draft.title,
            audience_portrait=draft.audience_portrait,
            platform_lane=draft.platform_lane,
            language_mode=draft.language_mode,
            funnel_role=draft.funnel_role,
            workflow_stage="revision_needed",
            review_decision="pending",
            linked_draft_id=draft.draft_id,
            revision_requested_at=action.decided_at,
            review_notes=action.notes,
        )
        archived_draft = reviewed_draft.model_copy(
            update={
                "workflow_stage": "archived",
                "archived": True,
            }
        )
        events.append(
            _build_event(
                event_name="brief_revision_requested",
                entity_type="brief",
                entity_id=draft.linked_brief_id or "unlinked_brief",
                triggered_at=action.decided_at,
                draft_id=draft.draft_id,
                brief_id=draft.linked_brief_id,
            )
        )
        return ApprovalResult(
            updated_draft=archived_draft,
            brief_update=brief_update,
            events=events,
        )

    archived_draft = reviewed_draft.model_copy(
        update={
            "workflow_stage": "archived",
            "archived": True,
        }
    )
    events.append(
        _build_event(
            event_name="draft_archived",
            entity_type="draft",
            entity_id=archived_draft.draft_id,
            triggered_at=action.decided_at,
            draft_id=archived_draft.draft_id,
        )
    )
    return ApprovalResult(
        updated_draft=archived_draft,
        events=events,
    )


def build_calendar_item(
    draft: DraftRecord,
    approved_at: str,
) -> CalendarItem:
    return CalendarItem(
        calendar_item_id=f"cal_{draft.draft_id}",
        source_draft_id=draft.draft_id,
        title=draft.title,
        platform=draft.platform,
        platform_lane=draft.platform_lane,
        language_mode=draft.language_mode,
        working_language=draft.working_language,
        publish_language=draft.publish_language,
        audience_portrait=draft.audience_portrait,
        voice_register_used=draft.voice_register,
        funnel_role=draft.funnel_role,
        final_text_ru=draft.draft_text_ru,
        final_text_en=draft.draft_text_en,
        approval_status="approved",
        approval_decided_at=approved_at,
    )


def _build_event(
    event_name: EventName,
    entity_type: EventEntityType,
    entity_id: str,
    triggered_at: str,
    draft_id: str | None = None,
    brief_id: str | None = None,
    calendar_item_id: str | None = None,
    payload_ref: str | None = None,
) -> OrchestrationEvent:
    return OrchestrationEvent(
        event_name=event_name,
        entity_type=entity_type,
        entity_id=entity_id,
        status="completed",
        triggered_at=triggered_at,
        draft_id=draft_id,
        brief_id=brief_id,
        calendar_item_id=calendar_item_id,
        payload_ref=payload_ref,
    )


def _next_draft_id(draft: DraftRecord) -> str:
    return f"{draft.draft_id}_v{draft.version + 1}"
