from __future__ import annotations

from dataclasses import dataclass

from content_engine.models.brief_builder import BriefBuilderResult, WorkflowABrief, WorkflowBBrief
from content_engine.models.content_factory import ContentFactoryRunResult, HumanReviewAsset
from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import ProducerContext, ProducerOutput
from content_engine.services.brief_builder import build_briefs
from content_engine.services.opportunity_queue import OpportunityQueueResult, process_opportunity_queue
from content_engine.services.producer import run_producer_workflow


@dataclass(frozen=True, slots=True)
class ContentFactoryDryRunResult:
    producer_output: ProducerOutput
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
    final_text = (
        f"Draft placeholder: {brief.opening_direction} "
        f"{brief.core_idea} Brief Builder prepared this for Writer Entity; final copy is not generated in dry-run."
    )
    internal_ru_master = None
    if brief.selected_platform == "linkedin":
        internal_ru_master = (
            f"RU master placeholder: {brief.core_idea}. "
            "LinkedIn final copy must be written in English after Writer Entity runs."
        )
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
        approval_status="needs_revision",
        final_text=final_text,
        internal_ru_master=internal_ru_master,
        editor_score=0.0,
        revision_notes=["Dry-run asset: route to Writer Entity before human approval."],
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
    selected_hook = brief.source_hook or brief.opening_direction
    script = (
        f"{selected_hook}\n"
        f"{brief.core_idea}\n"
        "Script placeholder: Workflow A script generation has not run in this dry-run."
    )
    filming_card = (
        f"Filming card placeholder for {brief.selected_platform}: "
        f"{brief.production_intent}"
    )
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
        selected_hook=selected_hook,
        script=script,
        filming_card=filming_card,
        editor_score=0.0,
        revision_notes=["Dry-run asset: route to Workflow A script generation before human approval."],
        source_refs=_source_refs(brief),
        season_id=brief.season_id,
        episode_id=brief.episode_id,
        scene_id=brief.scene_id,
        created_at=created_at,
    )


def _source_refs(brief: WorkflowABrief | WorkflowBBrief) -> list[str]:
    refs: list[str] = []
    for boundary in brief.factual_boundaries:
        prefix = "Evidence ref: "
        if boundary.startswith(prefix):
            refs.append(boundary.removeprefix(prefix))
    return refs


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
