from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from content_engine.models.hook_research import (
    ApprovedWorkflowAHandoff,
    HookOpportunity,
    HookResearchBlockedResult,
    HookResearchOutcomeBoard,
    ProducerHookSearchTask,
    is_workflow_a_eligible_hook,
)


def build_hook_research_outcome_board(
    *,
    producer_hook_search_task: ProducerHookSearchTask | Mapping[str, Any] | None = None,
    **board_payload: Any,
) -> HookResearchOutcomeBoard | HookResearchBlockedResult:
    """Build the producer-directed Workflow A hook research board.

    This is the guarded entry point for hook research. A missing or invalid
    ProducerHookSearchTask returns an explicit blocked state instead of
    silently running broad discovery.
    """

    task = _coerce_task(producer_hook_search_task)
    if isinstance(task, HookResearchBlockedResult):
        return task
    if not board_payload:
        return HookResearchBlockedResult(
            blocked_reason="PRODUCER_HOOK_SEARCH_TASK_INVALID",
            message="HookResearchOutcomeBoard requires board payload after ProducerHookSearchTask validation.",
        )

    try:
        hook_opportunities = _coerce_hooks(board_payload.get("hook_opportunities", []))
    except (TypeError, ValidationError, ValueError) as exc:
        return HookResearchBlockedResult(
            blocked_reason="PRODUCER_HOOK_SEARCH_TASK_INVALID",
            message=f"HookResearchOutcomeBoard cannot be built from incomplete hook opportunity evidence: {exc}",
        )
    board_payload["producer_hook_search_task"] = task
    board_payload["hook_opportunities"] = hook_opportunities
    if not board_payload.get("approved_for_workflow_a"):
        board_payload["approved_for_workflow_a"] = [
            _approved_handoff_from_hook(hook) for hook in hook_opportunities if is_workflow_a_eligible_hook(hook)
        ]
    if not board_payload.get("rejected_or_held"):
        board_payload["rejected_or_held"] = [
            _rejected_or_held_row(hook) for hook in hook_opportunities if not is_workflow_a_eligible_hook(hook)
        ]
    try:
        return HookResearchOutcomeBoard(**board_payload)
    except (TypeError, ValidationError, ValueError) as exc:
        return HookResearchBlockedResult(
            blocked_reason="PRODUCER_HOOK_SEARCH_TASK_INVALID",
            message=f"HookResearchOutcomeBoard cannot be built from incomplete hook research evidence: {exc}",
        )


def calculate_video_engagement_score(metrics: Mapping[str, int]) -> float:
    """Weighted public engagement score used to rank video hook candidates."""

    return (
        metrics.get("likes", 0)
        + metrics.get("comments", 0) * 4
        + metrics.get("shares", 0) * 5
        + metrics.get("saves", 0) * 5
        + metrics.get("views", 0) * 0.02
        + metrics.get("video_views", 0) * 0.02
    )


def format_hook_research_outcome_board_markdown(
    board: HookResearchOutcomeBoard | HookResearchBlockedResult,
) -> str:
    if isinstance(board, HookResearchBlockedResult):
        return "\n".join(
            [
                "# HookResearchOutcomeBoard",
                "",
                "## BLOCKED",
                f"Reason: {board.blocked_reason}",
                board.message,
            ]
        )

    header = board.board_header
    task = board.producer_hook_search_task
    lines = [
        "# HookResearchOutcomeBoard",
        "",
        "## 1. Board Header",
        "| Field | Value |",
        "|---|---|",
        f"| Board ID | {header.board_id} |",
        f"| Status | {header.status} |",
        f"| Workflow Route | {header.workflow_route} |",
        f"| Season | {header.season_title} |",
        f"| Monthly Storyline | {header.monthly_storyline} |",
        f"| Content Line | {header.content_line} |",
        "",
        "## 2. Producer Hook Search Task",
        "| Field | Value |",
        "|---|---|",
        f"| Directive ID | {task.directive_id} |",
        f"| Search Goal | {task.search_goal} |",
        f"| Target Audience | {task.target_audience} |",
        f"| Core Pain | {task.core_pain} |",
        f"| Core Desire | {task.core_desire} |",
        f"| Core Tension | {task.core_tension} |",
        "",
        "## 3. Research Scope & Filters",
        f"- Queries: {', '.join(board.research_scope.search_queries_used)}",
        f"- Platforms: {', '.join(board.research_scope.platform_filters)}",
        f"- Date filter: {board.research_scope.date_filter}",
        f"- Compliance: {', '.join(board.research_scope.compliance_filter)}",
        "",
        "## 4. Search Summary",
        "| Metric | Value |",
        "|---|---:|",
        f"| Sources scanned | {board.search_summary.sources_scanned} |",
        f"| Raw candidates | {board.search_summary.raw_candidates_collected} |",
        f"| Filtered hook opportunities | {board.search_summary.filtered_hook_opportunities} |",
        f"| Top priority hooks | {board.search_summary.top_priority_hooks} |",
        "",
        "## 5. Source Evidence Log",
        "| Evidence | Platform | Source URL | Signal | Boundary |",
        "|---|---|---|---|---|",
    ]
    for evidence in board.source_evidence_log:
        lines.append(
            "| "
            f"{evidence.evidence_ref} | "
            f"{evidence.source_platform} | "
            f"{evidence.source_url_or_internal_ref} | "
            f"{evidence.performance_signal_type} | "
            f"{evidence.reuse_boundary} |"
        )

    lines.extend(
        [
            "",
            "## 6. Hook Opportunities",
            "| Priority | Status | Mode | Source URL | Metrics | Producer Topic | Hook Mechanic | Adapted Hook for Jane | First Frame Text | Video Angle | Why It Might Work | Risk | Score | Human Decision | Next Action |",
            "|---:|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|",
        ]
    )
    for hook in board.hook_opportunities:
        lines.append(
            "| "
            f"{hook.priority_rank} | "
            f"{hook.decision_status} | "
            f"{hook.input_mode} | "
            f"{hook.source_video_url or '-'} | "
            f"{_format_metrics(hook.observed_engagement_metrics)} | "
            f"{hook.producer_topic} | "
            f"{hook.hook_mechanic} | "
            f"{hook.adapted_hook_for_jane} | "
            f"{hook.first_frame_text} | "
            f"{hook.video_angle} | "
            f"{hook.why_it_performed} | "
            f"{hook.risk_level} | "
            f"{hook.final_priority_score:.2f} | "
            f"{hook.human_decision or '-'} | "
            f"{hook.next_action or '-'} |"
        )

    lines.extend(
        [
            "",
            "## 7. Expanded Hook Cards",
        ]
    )
    for card in board.expanded_hook_cards:
        lines.extend(
            [
                f"### {card.hook_id}",
                f"- Pattern: {card.extracted_pattern}",
                f"- Jane hook: {card.jane_adapted_hook}",
                f"- Visual opening: {card.visual_opening}",
                f"- CTA direction: {card.cta_direction}",
                f"- Recommended decision: {card.recommended_decision}",
            ]
        )

    lines.extend(
        [
            "",
            "## 8. Approved For Workflow A",
            "| Hook | Opportunity | Status |",
            "|---|---|---|",
        ]
    )
    for handoff in board.approved_for_workflow_a:
        lines.append(
            f"| {handoff.approved_hook_id} | {handoff.approved_opportunity_id} | {handoff.workflow_a_brief_status} |"
        )
    lines.extend(
        [
            "",
            "## 9. QA Report",
            f"- Status: {board.qa_report.qa_status}",
            f"- Decision rules enforced: {board.qa_report.decision_rules_enforced}",
            f"- Workflow boundary OK: {board.qa_report.workflow_boundary_ok}",
            "",
            "## 10. Codex Notes",
            *[f"- {note}" for note in board.codex_runtime_notes],
        ]
    )
    return "\n".join(lines)


def _coerce_task(
    task: ProducerHookSearchTask | Mapping[str, Any] | None,
) -> ProducerHookSearchTask | HookResearchBlockedResult:
    if task is None:
        return HookResearchBlockedResult(
            blocked_reason="PRODUCER_HOOK_SEARCH_TASK_MISSING",
            message="Research Agent cannot search for hooks without a producer-approved task.",
        )
    if isinstance(task, ProducerHookSearchTask):
        return task
    try:
        return ProducerHookSearchTask(**dict(task))
    except (TypeError, ValidationError, ValueError) as exc:
        return HookResearchBlockedResult(
            blocked_reason="PRODUCER_HOOK_SEARCH_TASK_INVALID",
            message=f"Research Agent cannot search for hooks with an invalid producer task: {exc}",
        )


def _coerce_hooks(values: object) -> list[HookOpportunity]:
    hooks: list[HookOpportunity] = []
    if not isinstance(values, list):
        raise ValueError("hook_opportunities must be a list")
    for value in values:
        if isinstance(value, HookOpportunity):
            hooks.append(value)
        elif isinstance(value, Mapping):
            hooks.append(HookOpportunity(**dict(value)))
        else:
            raise ValueError("hook_opportunities must contain HookOpportunity objects or dictionaries")
    return hooks


def _approved_handoff_from_hook(hook: HookOpportunity) -> ApprovedWorkflowAHandoff:
    approved_opportunity_id = hook.opportunity_id or f"hook_opp_{hook.hook_id}"
    return ApprovedWorkflowAHandoff(
        approved_hook_id=hook.hook_id,
        approved_opportunity_id=approved_opportunity_id,
        directive_id=hook.directive_id,
        season_id=hook.season_id,
        episode_id=hook.episode_id,
        scene_id=hook.scene_id,
        selected_hook=hook.adapted_hook_for_jane,
        first_frame_text=hook.first_frame_text,
        video_angle=hook.video_angle,
        producer_context={
            "monthly_storyline": hook.monthly_storyline,
            "content_line": hook.content_line,
            "scene_type": hook.scene_type,
            "plot_function": hook.plot_function,
            "sales_intensity": hook.sales_intensity,
            "producer_topic": hook.producer_topic,
            "target_audience": hook.target_audience,
            "core_pain": hook.core_pain,
            "core_desire": hook.core_desire,
            "core_tension": hook.core_tension,
            "desired_cta_direction": hook.desired_cta_direction,
        },
        source_context={
            "input_mode": hook.input_mode,
            "source_item_refs": hook.source_item_refs,
            "source_platform": hook.source_platform,
            "source_type": hook.source_type,
            "creator_archetype": hook.creator_archetype,
            "performance_signal": hook.performance_signal,
            "performance_signal_strength": hook.performance_signal_strength,
            "source_video_url": hook.source_video_url,
            "observed_source_hook": hook.observed_source_hook,
            "observed_first_frame_text": hook.observed_first_frame_text,
            "observed_engagement_metrics": hook.observed_engagement_metrics,
            "engagement_score": hook.engagement_score,
            "engagement_rank": hook.engagement_rank,
            "scan_batch_size": hook.scan_batch_size,
            "engagement_selection_reason": hook.engagement_selection_reason,
            "source_relevance_score": hook.source_relevance_score,
            "source_confidence_score": hook.source_confidence_score,
            "why_it_performed": hook.why_it_performed,
            "hook_mechanic": hook.hook_mechanic,
            "producer_original_basis": hook.producer_original_basis,
            "risk_level": hook.risk_level,
            "risk_notes": hook.risk_notes,
        },
        evidence_refs=hook.evidence_refs,
        factual_boundaries=[
            "Use only approved HookResearchOutcomeBoard data.",
            "Workflow A must not perform research.",
            "Do not create publish queue, scheduler, auto-posting, or final platform captions.",
            "Do not copy source wording, story, creator identity, or visual sequence.",
            f"Source video URL: {hook.source_video_url}"
            if hook.source_video_url
            else "Producer-original hook; no external source URL.",
            f"Public metrics: {_format_metrics(hook.observed_engagement_metrics)}",
            hook.reuse_boundary,
            hook.risk_notes,
        ],
        reuse_boundary=hook.reuse_boundary,
        cta_direction=hook.cta_direction,
        workflow_a_brief_status="READY_TO_BUILD",
    )


def _rejected_or_held_row(hook: HookOpportunity) -> dict[str, Any]:
    return {
        "hook_id": hook.hook_id,
        "human_decision": hook.human_decision,
        "qa_status": hook.qa_status,
        "risk_level": hook.risk_level,
        "next_action": hook.next_action,
    }


def _format_metrics(metrics: Mapping[str, int]) -> str:
    if not metrics:
        return "-"
    ordered_keys = ["views", "video_views", "likes", "comments", "shares", "saves"]
    parts = [f"{key}={metrics[key]}" for key in ordered_keys if metrics.get(key) is not None]
    parts.extend(
        f"{key}={value}"
        for key, value in sorted(metrics.items())
        if key not in ordered_keys and value is not None
    )
    return ", ".join(parts) if parts else "-"


__all__ = [
    "build_hook_research_outcome_board",
    "calculate_video_engagement_score",
    "format_hook_research_outcome_board_markdown",
]
