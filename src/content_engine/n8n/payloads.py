from __future__ import annotations

from typing import Any

from content_engine.models.approval import ApprovalResult, CalendarItem, DraftRecord, OrchestrationEvent
from content_engine.models.workflow_a import FilmingCard, VideoHook, VideoPublishItem, VideoScript
from content_engine.models.workflow_b import BriefRecord


Payload = dict[str, Any]


def build_review_gate_envelope(result: ApprovalResult) -> Payload:
    route = _resolve_route(result)
    return {
        "workflow": "review_gate",
        "route": route,
        "draft": _serialize_draft(result.updated_draft),
        "next_draft": _serialize_draft(result.next_draft) if result.next_draft else None,
        "calendar_item": _serialize_calendar_item(result.calendar_item) if result.calendar_item else None,
        "brief_update": _serialize_brief(result.brief_update) if result.brief_update else None,
        "events": [_serialize_event(event) for event in result.events],
    }


def build_telegram_notification_payload(envelope: Payload) -> Payload:
    route = envelope["route"]
    draft = envelope["draft"]
    title = draft["title"]
    platform = draft["platform"]

    if route == "approved":
        message = f"Ready to publish: {title} [{platform}]"
    elif route == "needs_rewrite":
        next_draft = envelope["next_draft"] or {}
        message = f"Rewrite version {next_draft.get('version', '?')} ready: {title}"
    elif route == "re_brief":
        message = f"Brief revision needed: {title}"
    else:
        message = f"Draft archived: {title}"

    return {
        "channel": "telegram",
        "route": route,
        "draft_id": draft["draft_id"],
        "message": message,
    }


# ---------------------------------------------------------------------------
# Workflow A — Video Pipeline
# ---------------------------------------------------------------------------

def build_video_script_envelope(script: VideoScript, hook: VideoHook) -> Payload:
    return {
        "workflow": "video_pipeline",
        "route": "script_ready",
        "script": _serialize_script(script),
        "hook": _serialize_hook(hook),
    }


def build_video_filming_notification(envelope: Payload) -> Payload:
    script = envelope["script"]
    return {
        "channel": "telegram",
        "route": "script_ready",
        "script_id": script["script_id"],
        "message": f"New script ready to film: {script['title']} [{script['platform']}] — priority {script['filming_priority']}",
    }


def build_video_published_envelope(item: VideoPublishItem) -> Payload:
    return {
        "workflow": "video_pipeline",
        "route": "video_published",
        "publish_item": _serialize_publish_item(item),
    }


def build_video_published_notification(envelope: Payload) -> Payload:
    item = envelope["publish_item"]
    publish_date = item.get("publish_date") or "unscheduled date"
    return {
        "channel": "telegram",
        "route": "video_published",
        "publish_item_id": item["publish_item_id"],
        "message": f"Video published: {item['platform']} on {publish_date}",
    }


def _serialize_script(script: VideoScript) -> Payload:
    return {
        "script_id": script.script_id,
        "source_item_id": script.source_item_id,
        "title": script.title,
        "platform": script.platform,
        "hook_text": script.hook_text,
        "script_text": script.script_text,
        "cta": script.cta,
        "filming_priority": script.filming_priority,
        "status": script.status,
    }


def _serialize_hook(hook: VideoHook) -> Payload:
    return {
        "hook_id": hook.hook_id,
        "hook_type": hook.hook_type,
        "hook_text": hook.hook_text,
        "platform": hook.platform,
        "score": hook.score,
        "angle": hook.angle,
    }


def _serialize_publish_item(item: VideoPublishItem) -> Payload:
    return {
        "publish_item_id": item.publish_item_id,
        "linked_script_id": item.linked_script_id,
        "platform": item.platform,
        "caption": item.caption,
        "publish_date": item.publish_date,
        "status": item.status,
    }


def _resolve_route(result: ApprovalResult) -> str:
    decision = result.updated_draft.review_decision
    if decision in {"approved", "needs_rewrite", "re_brief", "deleted"}:
        return decision
    return "pending"


def _serialize_draft(draft: DraftRecord) -> Payload:
    return {
        "draft_id": draft.draft_id,
        "title": draft.title,
        "platform": draft.platform,
        "platform_lane": draft.platform_lane,
        "version": draft.version,
        "workflow_stage": draft.workflow_stage,
        "review_decision": draft.review_decision,
        "review_notes": draft.review_notes,
        "parent_draft_id": draft.parent_draft_id,
        "linked_brief_id": draft.linked_brief_id,
        "linked_calendar_id": draft.linked_calendar_id,
        "working_language": draft.working_language,
        "publish_language": draft.publish_language,
        "draft_text_ru": draft.draft_text_ru,
        "draft_text_en": draft.draft_text_en,
        "archived": draft.archived,
    }


def _serialize_calendar_item(item: CalendarItem) -> Payload:
    return {
        "calendar_item_id": item.calendar_item_id,
        "source_draft_id": item.source_draft_id,
        "title": item.title,
        "platform": item.platform,
        "platform_lane": item.platform_lane,
        "working_language": item.working_language,
        "publish_language": item.publish_language,
        "final_text_ru": item.final_text_ru,
        "final_text_en": item.final_text_en,
        "approval_status": item.approval_status,
        "approval_decided_at": item.approval_decided_at,
    }


def _serialize_brief(brief: BriefRecord) -> Payload:
    return {
        "brief_id": brief.brief_id,
        "title": brief.title,
        "audience_portrait": brief.audience_portrait,
        "platform_lane": brief.platform_lane,
        "language_mode": brief.language_mode,
        "funnel_role": brief.funnel_role,
        "workflow_stage": brief.workflow_stage,
        "review_decision": brief.review_decision,
        "linked_draft_id": brief.linked_draft_id,
        "revision_requested_at": brief.revision_requested_at,
        "review_notes": brief.review_notes,
    }


def _serialize_event(event: OrchestrationEvent) -> Payload:
    return {
        "event_name": event.event_name,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "status": event.status,
        "triggered_at": event.triggered_at,
        "draft_id": event.draft_id,
        "brief_id": event.brief_id,
        "calendar_item_id": event.calendar_item_id,
        "payload_ref": event.payload_ref,
    }
