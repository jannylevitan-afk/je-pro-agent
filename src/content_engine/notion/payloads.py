from __future__ import annotations

from typing import Any

from content_engine.models.analytics import ContentPerformanceRecord, DecisionMetrics, FeedbackSignal
from content_engine.models.approval import CalendarItem, DraftRecord, OrchestrationEvent
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_a import FilmingCard, VideoPublishItem, VideoScript
from content_engine.models.workflow_b import BriefRecord, IdeaCandidate, InsightCard


PropertyPayload = dict[str, Any]


def build_draft_properties(draft: DraftRecord) -> PropertyPayload:
    return {
        "Draft ID": _rich_text(draft.draft_id),
        "Title": _title(draft.title),
        "Draft text RU": _rich_text(draft.draft_text_ru),
        "Draft text EN": _rich_text(draft.draft_text_en),
        "Platform": _select(draft.platform),
        "Platform lane": _select(draft.platform_lane),
        "Language mode": _select(draft.language_mode),
        "Audience portrait": _select(draft.audience_portrait),
        "Voice register": _select(draft.voice_register),
        "Funnel role": _select(draft.funnel_role),
        "Version": _number(draft.version),
        "Working language": _select(draft.working_language),
        "Publish language": _select(draft.publish_language),
        "Workflow stage": _select(draft.workflow_stage),
        "Review decision": _select(draft.review_decision),
        "Review Notes": _rich_text(draft.review_notes),
        "Parent draft": _reference_id(draft.parent_draft_id),
        "Review requested at": _date(draft.review_requested_at),
        "Approval decided at": _date(draft.approval_decided_at),
        "AI edited": _checkbox(draft.ai_edited),
        "7-point test passed": _checkbox(draft.seven_point_test_passed),
        "Factual safety": _select(draft.factual_safety),
        "Linked brief": _reference_id(draft.linked_brief_id),
        "Linked calendar": _reference_id(draft.linked_calendar_id),
        "Archived": _checkbox(draft.archived),
        "Writer preflight status": _select(draft.writer_preflight_status),
        "Writer risk flags": _rich_text(_join_lines(draft.writer_risk_flags)),
        "Writer selected idea": _rich_text(draft.writer_selected_idea),
        "Hook options": _rich_text(_join_lines(draft.writer_hook_options)),
        "CTA options": _rich_text(_join_lines(draft.writer_cta_options)),
        "Writer QA Report": _rich_text(draft.writer_qa_report),
        "Writer human review required": _checkbox(draft.writer_human_review_required),
        "Final Content Asset": _rich_text(draft.final_content_asset),
    }


def build_brief_properties(brief: BriefRecord) -> PropertyPayload:
    reference_sources = "\n".join(brief.reference_sources) if brief.reference_sources else None
    return {
        "Brief ID": _rich_text(brief.brief_id),
        "Title": _title(brief.title),
        "Audience portrait": _select(brief.audience_portrait),
        "Platform lane": _select(brief.platform_lane),
        "Language mode": _select(brief.language_mode),
        "Funnel role": _select(brief.funnel_role),
        "Workflow stage": _select(brief.workflow_stage),
        "Review decision": _select(brief.review_decision),
        "Linked draft": _reference_id(brief.linked_draft_id),
        "Revision requested at": _date(brief.revision_requested_at),
        "Review notes": _rich_text(brief.review_notes),
        "Source rigor": _select(brief.source_rigor),
        "Reference sources": _rich_text(reference_sources),
    }


def build_calendar_properties(calendar_item: CalendarItem) -> PropertyPayload:
    return {
        "Platform": _select(calendar_item.platform),
        "Platform lane": _select(calendar_item.platform_lane),
        "Language mode": _select(calendar_item.language_mode),
        "Working language": _select(calendar_item.working_language),
        "Publish language": _select(calendar_item.publish_language),
        "Audience portrait": _select(calendar_item.audience_portrait),
        "Voice register used": _select(calendar_item.voice_register_used),
        "Pillar": _select(calendar_item.pillar),
        "Funnel role": _select(calendar_item.funnel_role),
        "Hook": _rich_text(calendar_item.hook),
        "Final text RU": _rich_text(calendar_item.final_text_ru),
        "Final text EN": _rich_text(calendar_item.final_text_en),
        "Source draft": _reference_id(calendar_item.source_draft_id),
        "Publish date target": _date(calendar_item.publish_date_target),
        "Approval status": _select(calendar_item.approval_status),
        "Approval decided at": _date(calendar_item.approval_decided_at),
        "Repurpose status": _select(None),
    }


def build_orchestration_event_properties(event: OrchestrationEvent) -> PropertyPayload:
    return {
        "Event name": _select(event.event_name),
        "Entity type": _select(event.entity_type),
        "Entity ID": _rich_text(event.entity_id),
        "Status": _select(event.status),
        "Triggered at": _date(event.triggered_at),
        "Draft ID": _reference_id(event.draft_id),
        "Brief ID": _reference_id(event.brief_id),
        "Calendar item ID": _reference_id(event.calendar_item_id),
        "Payload ref": _rich_text(event.payload_ref),
    }


def build_source_properties(source_item: SourceItem) -> PropertyPayload:
    title = f"{source_item.source_name}:{source_item.external_item_id}"
    return {
        "Title": _title(title),
        "Platform": _select(source_item.source_type),
        "Raw text": _rich_text(source_item.transcript_text),
        "External item ID": _rich_text(source_item.external_item_id),
        "Dedupe key": _rich_text(source_item.dedupe_key),
        "Content hash": _rich_text(source_item.content_hash),
        "Ingestion status": _select(source_item.processing_state),
    }


def build_insight_properties(insight: InsightCard) -> PropertyPayload:
    return {
        "Topic": _rich_text(insight.content_theme),
        "Angle": _rich_text(insight.useful_lesson),
        "Audience portrait": _select(insight.audience),
        "Narrative type": _select(insight.narrative_type),
        "Emotional trigger": _rich_text(insight.emotional_trigger),
        "Reuse score": _number(insight.reuse_score),
    }


def build_idea_properties(
    idea: IdeaCandidate,
    gate_passed: bool,
    status: str,
) -> PropertyPayload:
    return {
        "Title": _title(idea.working_title),
        "Platform": _select(idea.target_platform),
        "Platform lane": _select(idea.platform_lane),
        "Language mode": _select(idea.language_mode),
        "Funnel role": _select(idea.funnel_role),
        "Audience portrait": _select(idea.target_audience),
        "Emotional hook": _rich_text(idea.emotional_hook),
        "Desired reaction": _rich_text(idea.desired_reaction),
        "Gate passed": _checkbox(gate_passed),
        "Status": _select(status),
    }


def build_content_performance_properties(
    record: ContentPerformanceRecord,
    metrics: DecisionMetrics,
) -> PropertyPayload:
    return {
        "Linked content item": _reference_id(record.linked_content_item_id),
        "Platform": _select(record.platform),
        "Reach": _number(record.reach),
        "Impressions": _number(record.impressions),
        "Saves": _number(record.saves),
        "Shares": _number(record.shares),
        "Comments": _number(record.comments),
        "Profile visits": _number(record.profile_visits),
        "DMs received": _number(record.dms_received),
        "Inquiry type": _select(record.inquiry_type),
        "Likes": _number(record.likes),
        "Engagement rate": _number(metrics.engagement_rate),
        "CTR": _number(metrics.ctr),
        "Attribution model": _select(record.attribution_model),
        "Deal influenced": _checkbox(record.deal_influenced),
        "Performance tier": _select(record.performance_tier),
    }


def build_feedback_signal_properties(signal: FeedbackSignal) -> PropertyPayload:
    return {
        "Signal scope": _select(signal.signal_scope),
        "Dimension value": _rich_text(signal.dimension_value),
        "Signal type": _select(signal.signal_type),
        "Performance tier": _select(signal.performance_tier),
        "Score": _number(signal.score),
        "Reason": _rich_text(signal.reason),
        "Applied": _checkbox(False),
    }


def _title(value: str | None) -> PropertyPayload:
    if value is None or value == "":
        return {"title": []}
    return {
        "title": [
            {
                "type": "text",
                "text": {"content": value},
            }
        ]
    }


def _rich_text(value: str | None) -> PropertyPayload:
    if value is None or value == "":
        return {"rich_text": []}
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": value},
            }
        ]
    }


def _select(value: str | None) -> PropertyPayload:
    if value is None or value == "":
        return {"select": None}
    return {"select": {"name": value}}


def _number(value: int | float | None) -> PropertyPayload:
    return {"number": value}


def _checkbox(value: bool) -> PropertyPayload:
    return {"checkbox": value}


def _date(value: str | None) -> PropertyPayload:
    if value is None or value == "":
        return {"date": None}
    return {"date": {"start": value}}


def _join_lines(values: list[str]) -> str | None:
    return "\n".join(values) if values else None


def _relation(value: str | None) -> PropertyPayload:
    if value is None or value == "":
        return {"relation": []}
    return {"relation": [{"id": value}]}


def _reference_id(value: str | None) -> PropertyPayload:
    return _rich_text(value)


def _url(value: str | None) -> PropertyPayload:
    return {"url": value}


# ---------------------------------------------------------------------------
# Workflow A — Video Pipeline
# ---------------------------------------------------------------------------

def build_script_properties(script: VideoScript) -> PropertyPayload:
    return {
        "Title": _title(script.title),
        "Hook": _rich_text(script.hook_text),
        "Platform": _select(script.platform),
        "Script text": _rich_text(script.script_text),
        "Filming priority": _number(script.filming_priority),
        "Status": _select(script.status),
    }


def build_filming_card_properties(card: FilmingCard) -> PropertyPayload:
    return {
        "Linked script": _reference_id(card.linked_script_id),
        "Shoot date": _date(card.shoot_date),
        "Filmed": _checkbox(card.filmed),
        "Raw file link": _url(card.raw_file_link),
    }


def build_video_publish_properties(item: VideoPublishItem) -> PropertyPayload:
    return {
        "Platform": _select(item.platform),
        "Publish date": _date(item.publish_date),
        "Caption": _rich_text(item.caption),
        "Status": _select(item.status),
    }
