from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, cast

from content_engine.context.workflow_b_rules import (
    WorkflowBDecision,
    expand_workflow_b_decisions,
    infer_narrative_type,
    infer_useful_lesson,
)
from content_engine.knowledge.kmd import KnowledgeStore
from content_engine.models.approval import DraftRecord
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_a import VideoPlatform
from content_engine.models.workflow_b import BriefRecord
from content_engine.notion.sync import (
    NotionClientLike,
    create_idea,
    create_insight,
    create_orchestration_event,
    upsert_brief,
    upsert_draft,
    upsert_source,
)
from content_engine.orchestration.video_gate import (
    VideoGateOrchestrationResult,
    VideoNotionTargets,
    orchestrate_script_ready,
)
from content_engine.services.approval import submit_for_review
from content_engine.services.draft import build_draft_bundle
from content_engine.services.editing import run_editorial_gate
from content_engine.services.routing import route_signal
from content_engine.services.workflow_a import (
    build_filming_card,
    build_video_intake_record,
    build_video_script,
    develop_video_hooks,
    select_best_hook,
)
from content_engine.services.workflow_b import (
    build_content_brief,
    build_idea_candidate,
    build_insight_card,
    gate_idea_candidate,
    normalize_source_item,
)
from content_engine.orchestration.targets import LivePipelineTargets


Route = Literal["workflow_a", "workflow_b", "both", "drop"]


@dataclass(frozen=True, slots=True)
class LivePipelineItemResult:
    source_item_id: str
    route: Route
    source_page_id: str
    insight_page_id: str | None
    idea_page_ids: list[str]
    brief_page_ids: list[str]
    draft_page_ids: list[str]
    event_page_ids: list[str]
    script_page_id: str | None
    filming_card_page_id: str | None
    video_n8n_envelope: dict[str, Any] | None = None
    video_telegram_notification: dict[str, Any] | None = None
    knowledge_file_paths: list[str] = field(default_factory=list)


class SourceCollector(Protocol):
    def collect(self) -> list[SourceItem]:
        ...


class WorkflowWriter(Protocol):
    def write_video_script(
        self,
        *,
        item: SourceItem,
        title: str,
        hook: str,
        body_points: list[str],
        cta: str,
    ) -> str:
        ...

    def write_workflow_b_draft(
        self,
        *,
        item: SourceItem,
        insight: Any,
        decision: WorkflowBDecision,
        brief: Any,
    ) -> Any:
        ...


def run_live_pipeline(
    client: NotionClientLike,
    targets: LivePipelineTargets,
    items: list[SourceItem],
    verified_facts: set[str],
    submitted_at: str,
    writer: WorkflowWriter | None = None,
    knowledge_store: KnowledgeStore | None = None,
) -> list[LivePipelineItemResult]:
    return [
        process_source_item(
            client=client,
            targets=targets,
            item=item,
            verified_facts=verified_facts,
            submitted_at=submitted_at,
            writer=writer,
            knowledge_store=knowledge_store,
        )
        for item in items
    ]


def run_collector_cycle(
    collector: SourceCollector,
    client: NotionClientLike,
    targets: LivePipelineTargets,
    verified_facts: set[str],
    submitted_at: str,
    writer: WorkflowWriter | None = None,
    knowledge_store: KnowledgeStore | None = None,
) -> list[LivePipelineItemResult]:
    return run_live_pipeline(
        client=client,
        targets=targets,
        items=collector.collect(),
        verified_facts=verified_facts,
        submitted_at=submitted_at,
        writer=writer,
        knowledge_store=knowledge_store,
    )


def process_source_item(
    client: NotionClientLike,
    targets: LivePipelineTargets,
    item: SourceItem,
    verified_facts: set[str],
    submitted_at: str,
    writer: WorkflowWriter | None = None,
    knowledge_store: KnowledgeStore | None = None,
) -> LivePipelineItemResult:
    source_response = upsert_source(client, targets.sources_database_id, item)
    source_page_id = _page_id(source_response)

    route: Route = cast(Route, route_signal(_summarize_signal(item)))

    script_page_id: str | None = None
    filming_card_page_id: str | None = None
    video_n8n_envelope: dict[str, Any] | None = None
    video_telegram_notification: dict[str, Any] | None = None
    knowledge_file_paths: list[str] = []
    if route in {"workflow_a", "both"}:
        knowledge_file_paths.extend(_write_workflow_material(knowledge_store, item, "workflow_a"))
        video_gate_result = _run_workflow_a(
            client=client,
            targets=targets,
            item=item,
            writer=writer,
        )
        script_page_id = video_gate_result.script_page_id
        filming_card_page_id = video_gate_result.filming_card_page_id
        video_n8n_envelope = video_gate_result.n8n_envelope
        video_telegram_notification = video_gate_result.telegram_notification

    insight_page_id: str | None = None
    idea_page_ids: list[str] = []
    brief_page_ids: list[str] = []
    draft_page_ids: list[str] = []
    event_page_ids: list[str] = []
    if route in {"workflow_b", "both"}:
        knowledge_file_paths.extend(_write_workflow_material(knowledge_store, item, "workflow_b"))
        (
            insight_page_id,
            idea_page_ids,
            brief_page_ids,
            draft_page_ids,
            event_page_ids,
        ) = _run_workflow_b(
            client=client,
            targets=targets,
            item=item,
            verified_facts=verified_facts,
            submitted_at=submitted_at,
            writer=writer,
        )

    return LivePipelineItemResult(
        source_item_id=item.item_id,
        route=route,
        source_page_id=source_page_id,
        insight_page_id=insight_page_id,
        idea_page_ids=idea_page_ids,
        brief_page_ids=brief_page_ids,
        draft_page_ids=draft_page_ids,
        event_page_ids=event_page_ids,
        script_page_id=script_page_id,
        filming_card_page_id=filming_card_page_id,
        video_n8n_envelope=video_n8n_envelope,
        video_telegram_notification=video_telegram_notification,
        knowledge_file_paths=knowledge_file_paths,
    )


def _write_workflow_material(
    knowledge_store: KnowledgeStore | None,
    item: SourceItem,
    workflow: Literal["workflow_a", "workflow_b"],
) -> list[str]:
    if knowledge_store is None:
        return []
    return [str(knowledge_store.write_source_material(item, workflow=workflow))]


def _run_workflow_a(
    client: NotionClientLike,
    targets: LivePipelineTargets,
    item: SourceItem,
    writer: WorkflowWriter | None,
) -> VideoGateOrchestrationResult:
    platform = _select_video_platform(item)
    intake = build_video_intake_record(item)
    hooks = develop_video_hooks(item, platform=platform)
    best_hook = select_best_hook(hooks)
    title = intake.title or _build_video_title(item)
    body_points = [
        _video_script_source_line(intake.spoken_transcript or infer_useful_lesson(item)),
        _video_metric_line(intake.metrics),
        "The real risk usually hides in legal structure, operations, and price illusion.",
        "Good video content should show the market logic before it shows the object.",
    ]
    script = build_video_script(
        hook=best_hook,
        title=title,
        body_points=body_points,
        cta="Save this before your next Bali property review.",
    )
    if writer is not None:
        script = script.model_copy(
            update={
                "script_text": writer.write_video_script(
                    item=item,
                    title=title,
                    hook=best_hook.hook_text,
                    body_points=body_points,
                    cta="Save this before your next Bali property review.",
                )
            }
        )
    card = build_filming_card(script, filming_priority=1)

    return orchestrate_script_ready(
        client=client,
        targets=VideoNotionTargets(
            scripts_database_id=targets.scripts_database_id,
            filming_cards_database_id=targets.filming_cards_database_id,
        ),
        script=script,
        hook=best_hook,
        filming_card=card,
    )


def _run_workflow_b(
    client: NotionClientLike,
    targets: LivePipelineTargets,
    item: SourceItem,
    verified_facts: set[str],
    submitted_at: str,
    writer: WorkflowWriter | None,
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    note = normalize_source_item(item)
    insight = build_insight_card(
        note=note,
        emotional_trigger=_emotional_trigger(item),
        useful_lesson=infer_useful_lesson(item),
        narrative_type=infer_narrative_type(item),
        reuse_score=_reuse_score(item),
    )
    insight_response = create_insight(client, targets.insights_database_id, insight)
    insight_page_id = _page_id(insight_response)

    idea_page_ids: list[str] = []
    brief_page_ids: list[str] = []
    draft_page_ids: list[str] = []
    event_page_ids: list[str] = []

    for decision in expand_workflow_b_decisions(item):
        idea = build_idea_candidate(
            insight=insight,
            platform=decision.platform,
            platform_lane=decision.platform_lane,
            language_mode="ru",
            funnel_role=decision.funnel_role,
            working_title=_build_working_title(item, decision),
            emotional_hook=decision.emotional_hook,
            desired_reaction=decision.desired_reaction,
            suggested_format=_suggested_format(decision),
        )
        gate_passed, failed_gates = gate_idea_candidate(
            {
                "audience_fit": True,
                "value_emotion": insight.reuse_score >= 2,
                "engagement_trigger": bool(decision.desired_reaction),
                "platform_lane_fit": True,
            }
        )
        idea_response = create_idea(
            client,
            targets.ideas_database_id,
            idea,
            gate_passed=gate_passed,
            status="ready" if gate_passed else "rejected",
        )
        idea_page_ids.append(_page_id(idea_response))
        if not gate_passed:
            continue

        reference_sources = _reference_sources(item, decision)
        brief = build_content_brief(
            insight=insight,
            platform=decision.platform,
            platform_lane=decision.platform_lane,
            funnel_role=decision.funnel_role,
            purpose=_purpose(decision),
            hook=_hook_line(item, decision),
            key_points=_key_points(item),
            cta_type=decision.cta_type,
            tone=decision.tone,
            length_target="medium",
            engagement_objective=decision.engagement_objective,
            fact_pack=_matching_fact_pack(item, verified_facts),
            source_rigor=decision.source_rigor,
            reference_sources=reference_sources,
        )
        brief_record = BriefRecord(
            brief_id=_brief_id(item, decision),
            title=_build_working_title(item, decision),
            audience_portrait=insight.audience,
            platform_lane=brief.platform_lane,
            language_mode=brief.working_language,
            funnel_role=brief.funnel_role,
            workflow_stage="brief_ready",
            review_decision="pending",
            source_rigor=brief.source_rigor,
            reference_sources=brief.reference_sources,
        )
        brief_response = upsert_brief(client, targets.briefs_database_id, brief_record)
        brief_page_ids.append(_page_id(brief_response))

        draft_text_ru = _draft_text_ru(item, insight, decision)
        draft_text_en = _draft_text_en(item, insight, decision)
        if writer is not None:
            writer_output = writer.write_workflow_b_draft(
                item=item,
                insight=insight,
                decision=decision,
                brief=brief,
            )
            draft_text_ru = writer_output.draft_text_ru
            draft_text_en = writer_output.draft_text_en

        draft_bundle = build_draft_bundle(
            brief=brief,
            draft_text_ru=draft_text_ru,
            voice_register=decision.tone,
            audience_portrait=insight.audience,
            draft_text_en=draft_text_en,
        )
        editing_result = run_editorial_gate(
            draft=draft_bundle,
            fact_claims=brief.fact_pack,
            verified_facts=verified_facts,
        )
        draft_record = DraftRecord(
            draft_id=_draft_id(item, decision),
            title=draft_bundle.title,
            platform=draft_bundle.platform,
            platform_lane=draft_bundle.platform_lane,
            language_mode="ru",
            working_language=draft_bundle.working_language,
            publish_language=draft_bundle.publish_language,
            audience_portrait=draft_bundle.audience_portrait,
            voice_register=draft_bundle.voice_register,
            funnel_role=draft_bundle.funnel_role,
            draft_text_ru=draft_bundle.draft_text_ru,
            draft_text_en=draft_bundle.draft_text_en,
            version=1,
            workflow_stage="ai_edited",
            review_decision="pending",
            ai_edited=True,
            seven_point_test_passed=editing_result.seven_point_passed,
            factual_safety=editing_result.factual_safety,
            linked_brief_id=brief_record.brief_id,
        )
        if draft_record.factual_safety == "blocked":
            draft_response = upsert_draft(client, targets.drafts_database_id, draft_record)
            draft_page_ids.append(_page_id(draft_response))
            continue

        submitted_draft, events = submit_for_review(
            draft=draft_record,
            submitted_at=submitted_at,
        )
        draft_response = upsert_draft(client, targets.drafts_database_id, submitted_draft)
        draft_page_ids.append(_page_id(draft_response))
        for event in events:
            event_response = create_orchestration_event(
                client,
                targets.events_database_id,
                event,
            )
            event_page_ids.append(_page_id(event_response))

    return (
        insight_page_id,
        idea_page_ids,
        brief_page_ids,
        draft_page_ids,
        event_page_ids,
    )


def _summarize_signal(item: SourceItem) -> dict[str, Any]:
    words = len(item.transcript_text.split())
    max_signal = max(item.engagement_signals.values(), default=0)
    relevance_score = 6
    if words >= 8:
        relevance_score += 1
    if max_signal >= 1000:
        relevance_score += 1
    if item.content_theme in {"boutique_hotels", "wellness_architecture", "marketing_cases"}:
        relevance_score += 1
    return {
        "relevance_score": min(relevance_score, 10),
        "is_video": bool(item.media_urls),
        "has_trend_hook": bool(item.media_urls) or max_signal >= 1000,
        "has_textual_depth": words >= 8,
    }


def _select_video_platform(item: SourceItem) -> VideoPlatform:
    prefix = item.source_type.split("_")[0]
    if prefix in {"instagram", "tiktok", "youtube", "linkedin"}:
        return prefix  # type: ignore[return-value]
    return "instagram"


def _build_video_title(item: SourceItem) -> str:
    return f"{item.content_theme.replace('_', ' ').title()} signal for {item.audience_segment}"


def _video_script_source_line(transcript: str) -> str:
    normalized = " ".join(transcript.split()).strip()
    if len(normalized) <= 220:
        return normalized
    return normalized[:219].rstrip() + "..."


def _video_metric_line(metrics: dict[str, int]) -> str:
    if not metrics:
        return "No public video metrics were available at collection time."
    return "Public video metrics: " + ", ".join(f"{key}={value}" for key, value in sorted(metrics.items()))


def _reuse_score(item: SourceItem) -> int:
    max_signal = max(item.engagement_signals.values(), default=0)
    if max_signal >= 5000:
        return 5
    if max_signal >= 1000:
        return 4
    if len(item.transcript_text.split()) >= 10:
        return 3
    return 2


def _emotional_trigger(item: SourceItem) -> str:
    audience_map = {
        "developer_investor": "status anxiety",
        "broker": "deal urgency",
        "architect_designer": "taste validation",
        "lifestyle_expat": "identity pull",
        "dreamer_woman": "future-self desire",
    }
    return audience_map.get(item.audience_segment, "status anxiety")


def _build_working_title(item: SourceItem, decision: WorkflowBDecision) -> str:
    theme = item.content_theme.replace("_", " ")
    lane = decision.platform_lane.replace("_", " ")
    return f"{theme.title()} -> {lane}"


def _suggested_format(decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "thought_leadership_post"
    if decision.platform_lane == "instagram_lifestyle":
        return "story_caption"
    return "carousel_caption"


def _purpose(decision: WorkflowBDecision) -> str:
    if decision.funnel_role == "affinity":
        return "Create emotional closeness and recognition."
    if decision.funnel_role == "authority":
        return "Build market trust through concrete insight."
    return "Trigger a meaningful next-step reaction."


def _hook_line(item: SourceItem, decision: WorkflowBDecision) -> str:
    if decision.platform_lane == "linkedin_b2b":
        return "The cheapest line item in Bali is often the most expensive strategic mistake."
    if decision.platform_lane == "instagram_lifestyle":
        return "Some projects change your mood before they change your spreadsheet."
    return "What looks cheap first is often the most expensive later."


def _key_points(item: SourceItem) -> list[str]:
    lesson = infer_useful_lesson(item).rstrip(".")
    return [
        lesson,
        "Legal structure changes the deal far more than brochure language suggests.",
        "Operations and positioning shape the real outcome after purchase.",
    ]


def _matching_fact_pack(item: SourceItem, verified_facts: set[str]) -> list[str]:
    transcript_lower = item.transcript_text.lower()
    matched = [
        fact
        for fact in sorted(verified_facts)
        if any(token in transcript_lower for token in fact.lower().split() if len(token) > 4)
    ]
    return matched[:3]


def _reference_sources(item: SourceItem, decision: WorkflowBDecision) -> list[str]:
    raw_sources = item.raw_payload.get("reference_sources")
    if isinstance(raw_sources, list):
        normalized = [str(source) for source in raw_sources if str(source).strip()]
        if decision.source_rigor == "market-critical":
            return normalized[:4] if len(normalized) >= 4 else _fallback_sources(item, 4)
        if decision.source_rigor == "expert":
            return normalized[:3] if len(normalized) >= 3 else _fallback_sources(item, 3)
        return normalized[:1]

    if decision.source_rigor == "market-critical":
        return _fallback_sources(item, 4)
    if decision.source_rigor == "expert":
        return _fallback_sources(item, 3)
    return []


def _fallback_sources(item: SourceItem, count: int) -> list[str]:
    suffixes = ["source", "context", "ops", "market", "evidence"]
    return [f"{item.source_url}#{suffixes[index]}" for index in range(count)]


def _draft_text_ru(item: SourceItem, insight: Any, decision: WorkflowBDecision) -> str:
    lesson = infer_useful_lesson(item)
    if decision.platform_lane == "instagram_lifestyle":
        return (
            f"{_hook_line(item, decision)}\n"
            f"{lesson}\n"
            "В таких проектах важна не только цифра. Важна версия жизни, в которую человек входит.\n"
            "Ты бы зашла в такой проект ради картинки или ради ощущения, что он меняет траекторию?"
        )
    if decision.platform_lane == "linkedin_b2b":
        return (
            f"{_hook_line(item, decision)}\n"
            f"{lesson}\n"
            "Для девелопера и инвестора это не вопрос вкуса. Это вопрос структуры сделки, позиционирования и доходности.\n"
            "Что чаще всего недооценивают на ранней стадии проекта?"
        )
    return (
        f"{_hook_line(item, decision)}\n"
        f"{lesson}\n"
        "Рынок наказывает не за отсутствие энтузиазма, а за слабую логику решения.\n"
        "Что ты бы проверил первым делом перед таким входом?"
    )


def _draft_text_en(item: SourceItem, insight: Any, decision: WorkflowBDecision) -> str | None:
    if decision.platform_lane != "linkedin_b2b":
        return None
    lesson = infer_useful_lesson(item).rstrip(".")
    return (
        f"{_hook_line(item, decision)}\n"
        f"{lesson}.\n"
        "For developers and investors, this is not a taste question. It is a structure, positioning, and yield question.\n"
        "What gets underestimated first in projects like this?"
    )


def _brief_id(item: SourceItem, decision: WorkflowBDecision) -> str:
    return f"brief_{item.item_id}_{decision.platform_lane}"


def _draft_id(item: SourceItem, decision: WorkflowBDecision) -> str:
    return f"draft_{item.item_id}_{decision.platform_lane}"


def _page_id(response: dict[str, Any]) -> str:
    page_id = response.get("id")
    if not isinstance(page_id, str) or not page_id:
        raise ValueError("Expected Notion response to include page id")
    return page_id
