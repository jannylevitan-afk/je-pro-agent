from __future__ import annotations

from dataclasses import dataclass

from content_engine.models.brief_builder import BriefBuilderResult, WorkflowABrief, WorkflowBBrief
from content_engine.models.content_factory import ContentFactoryRunResult, HumanReviewAsset
from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import ProducerContext, ProducerOutput
from content_engine.models.producer_output_contract import ReadableProducerOutput
from content_engine.models.writer_entity import EditorDiagnosis
from content_engine.services.brief_builder import build_briefs
from content_engine.services.opportunity_queue import OpportunityQueueResult, process_opportunity_queue
from content_engine.services.producer import run_producer_workflow
from content_engine.services.producer_output_contract import build_readable_producer_output
from content_engine.services.workflow_a import run_workflow_a_from_brief
from content_engine.services.writer_entity import build_final_content_asset, run_writer_entity_for_workflow_b_brief


@dataclass(frozen=True, slots=True)
class ContentFactoryDryRunResult:
    producer_output: ProducerOutput
    readable_producer_output: ReadableProducerOutput
    queue_result: OpportunityQueueResult
    briefs: list[BriefBuilderResult]
    human_review_assets: list[HumanReviewAsset]
    run_result: ContentFactoryRunResult


def run_content_factory_dry_run(
    *,
    context: ProducerContext,
    opportunities: list[OpportunityCandidate],
    run_id: str,
    created_at: str,
) -> ContentFactoryDryRunResult:
    """Run the new Producer -> Queue -> Brief Builder chain without live Search/Writer calls."""

    producer_output = run_producer_workflow(context, created_at=created_at)
    readable_producer_output = build_readable_producer_output(producer_output, context=context)
    first_episode = producer_output.episodes[0]
    first_scene_id = first_episode.scene_ids[0]
    queue_result = process_opportunity_queue(
        opportunities,
        season_id=producer_output.season.season_id,
        episode_id=first_episode.episode_id,
        scene_id=first_scene_id,
        created_at=created_at,
    )
    briefs = build_briefs(
        queue_result.approved,
        opportunities=[entry.candidate for entry in queue_result.queued],
        decisions=queue_result.decisions,
        scenes=producer_output.scenes,
        created_at=created_at,
    )
    human_review_assets = build_human_review_assets(briefs, created_at=created_at)
    run_result = ContentFactoryRunResult(
        run_id=run_id,
        status="completed",
        started_at=created_at,
        completed_at=created_at,
        research_handoff_count=0,
        opportunity_count=len(opportunities),
        producer_decision_count=len(queue_result.decisions),
        workflow_a_asset_count=sum(1 for asset in human_review_assets if asset.workflow == "workflow_a"),
        workflow_b_asset_count=sum(1 for asset in human_review_assets if asset.workflow == "workflow_b"),
        human_review_asset_count=len(human_review_assets),
        output_files=[
            "outputs/latest/opportunity_queue.json",
            "outputs/latest/producer_decisions.json",
            "outputs/latest/workflow_a_video_assets.json",
            "outputs/latest/workflow_b_text_assets.json",
            "outputs/latest/human_review_assets.json",
        ],
        warnings=_dry_run_warnings(queue_result),
    )
    return ContentFactoryDryRunResult(
        producer_output=producer_output,
        readable_producer_output=readable_producer_output,
        queue_result=queue_result,
        briefs=briefs,
        human_review_assets=human_review_assets,
        run_result=run_result,
    )


def build_human_review_assets(
    briefs: list[BriefBuilderResult],
    *,
    created_at: str,
) -> list[HumanReviewAsset]:
    return [_human_review_asset_from_brief(result, created_at=created_at) for result in briefs]


def _human_review_asset_from_brief(
    result: BriefBuilderResult,
    *,
    created_at: str,
) -> HumanReviewAsset:
    brief = result.brief
    if isinstance(brief, WorkflowABrief):
        return _workflow_a_asset(brief, created_at=created_at)
    return _workflow_b_asset(brief, created_at=created_at)


def _workflow_b_asset(
    brief: WorkflowBBrief,
    *,
    created_at: str,
) -> HumanReviewAsset:
    writer_output = run_writer_entity_for_workflow_b_brief(brief)
    final_asset = build_final_content_asset(
        writer_output=writer_output,
        content_id=f"content_{brief.brief_id}",
        title=brief.angle,
        platform=brief.selected_platform,
        pillar=brief.rubric,
        content_format="post",
        approval_status="review_ready",
        source_ids=_source_refs(brief) or [brief.source_item_id],
        insight_id=brief.opportunity_id,
        idea_id=writer_output.selected_idea.idea_id,
        brief_id=brief.brief_id,
        draft_id=f"draft_{brief.brief_id}",
        edit_version_id=f"edit_{brief.brief_id}_v1",
    )
    internal_ru_master = _internal_ru_master_for_linkedin(brief) if brief.selected_platform == "linkedin" else None
    revision_notes = [
        "Writer Entity generated from WorkflowBBrief.",
        *writer_output.qa_report.fixes_applied,
    ]
    if writer_output.qa_report.issues:
        revision_notes.extend(f"QA issue: {issue}" for issue in writer_output.qa_report.issues)
    return HumanReviewAsset(
        content_id=f"content_{brief.brief_id}",
        source_item_id=brief.source_item_id,
        opportunity_id=brief.opportunity_id,
        decision_id=brief.decision_id,
        brief_id=brief.brief_id,
        workflow="workflow_b",
        platform=brief.selected_platform,
        title=brief.angle,
        pillar=brief.rubric,
        audience_segment=brief.audience_segment,
        approval_status="approved_for_human_review" if writer_output.qa_report.passed else "needs_revision",
        final_text=final_asset.final_text,
        internal_ru_master=internal_ru_master,
        editor_score=_editor_score(writer_output.editor_diagnosis),
        revision_notes=revision_notes,
        source_refs=_source_refs(brief),
        season_id=brief.season_id,
        episode_id=brief.episode_id,
        scene_id=brief.scene_id,
        created_at=created_at,
    )


def _workflow_a_asset(
    brief: WorkflowABrief,
    *,
    created_at: str,
) -> HumanReviewAsset:
    video_asset = run_workflow_a_from_brief(brief)
    return HumanReviewAsset(
        content_id=f"content_{brief.brief_id}",
        source_item_id=brief.source_item_id,
        opportunity_id=brief.opportunity_id,
        decision_id=brief.decision_id,
        brief_id=brief.brief_id,
        workflow="workflow_a",
        platform=brief.selected_platform,
        title=brief.angle,
        pillar=brief.rubric,
        audience_segment=brief.audience_segment,
        approval_status="needs_revision",
        selected_hook=video_asset.selected_hook.hook_text,
        script=video_asset.script.script_text,
        filming_card=_format_filming_card(video_asset.filming_card.card_id, video_asset.filming_card.filming_priority),
        editor_score=round(video_asset.selected_hook.score / 10, 2),
        revision_notes=[
            "Workflow A generated from WorkflowABrief.",
            f"Selected hook type: {video_asset.selected_hook.hook_type}.",
            "Manual filming remains required.",
        ],
        source_refs=_source_refs(brief),
        season_id=brief.season_id,
        episode_id=brief.episode_id,
        scene_id=brief.scene_id,
        created_at=created_at,
    )


def _format_filming_card(card_id: str, priority: int) -> str:
    return "\n".join(
        [
            f"card_id: {card_id}",
            f"filming_priority: {priority}",
            "filmed: false",
            "manual_step: human records video",
        ]
    )


def _source_refs(brief: WorkflowABrief | WorkflowBBrief) -> list[str]:
    refs: list[str] = []
    for boundary in brief.factual_boundaries:
        prefix = "Evidence ref: "
        if boundary.startswith(prefix):
            refs.append(boundary.removeprefix(prefix))
    return refs


def _internal_ru_master_for_linkedin(brief: WorkflowBBrief) -> str:
    return "\n\n".join(
        [
            "Рабочая RU-версия для LinkedIn.",
            f"Угол: {brief.angle}.",
            f"Главная мысль: {brief.core_idea}",
            f"Адаптация Jane: {brief.jane_adaptation_instruction}",
            f"Основа источника: {brief.source_summary}",
            f"Что сработало: {brief.what_performed}",
        ]
    )


def _editor_score(diagnosis: EditorDiagnosis) -> float:
    raw_score = min(
        diagnosis.hook_score,
        diagnosis.clarity_score,
        diagnosis.emotional_score,
        diagnosis.voice_preservation_score,
        diagnosis.fact_safety_score,
    )
    return round(raw_score / 10, 2)


def _dry_run_warnings(queue_result: OpportunityQueueResult) -> list[str]:
    warnings: list[str] = []
    if queue_result.held_ids:
        warnings.append(f"held opportunities: {', '.join(queue_result.held_ids)}")
    if queue_result.rejected_ids:
        warnings.append(f"rejected opportunities: {', '.join(queue_result.rejected_ids)}")
    return warnings


__all__ = [
    "ContentFactoryDryRunResult",
    "build_human_review_assets",
    "run_content_factory_dry_run",
]
