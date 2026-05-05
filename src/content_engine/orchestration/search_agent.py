from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from content_engine.collectors.native import (
    Fetcher,
    NativeSourceTarget,
    collect_native_source_items,
    resolve_target_url,
)
from content_engine.knowledge.kmd import KnowledgeStore
from content_engine.models.source_item import SourceItem
from content_engine.models.hook_research import (
    HookResearchBlockedResult,
    HookResearchOutcomeBoard,
    ProducerHookSearchTask,
)
from content_engine.notion.sync import NotionClientLike
from content_engine.orchestration.live_pipeline import LivePipelineItemResult, WorkflowWriter, run_live_pipeline
from content_engine.orchestration.targets import LivePipelineTargets
from content_engine.services.analyst import WorkflowAnalyst
from content_engine.services.hook_research import build_hook_research_outcome_board


ComplianceStatus = Literal["allowed", "review", "blocked"]
RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class ComplianceCheck:
    target_handle: str
    platform: str
    source_url: str
    status: ComplianceStatus
    risk_level: RiskLevel
    reason: str
    collection_mode: str


@dataclass(frozen=True, slots=True)
class EvidenceLogEntry:
    item_id: str
    source_type: str
    route: str
    source_url: str
    timestamp: str
    raw_excerpt: str
    confidence_score: float


@dataclass(frozen=True, slots=True)
class SearchAgentReport:
    compliance_checks: list[ComplianceCheck]
    evidence_logs: list[EvidenceLogEntry]
    pipeline_results: list[LivePipelineItemResult]
    skipped_target_handles: list[str]
    dropped_item_ids: list[str]


def run_hook_research_agent(
    *,
    producer_hook_search_task: ProducerHookSearchTask | dict[str, object] | None,
    **board_payload: object,
) -> HookResearchOutcomeBoard | HookResearchBlockedResult:
    """Guarded Research Agent entry point for Workflow A hook boards.

    Hook research is producer-directed only. Without a valid
    ProducerHookSearchTask this returns an explicit blocked state and performs
    no discovery or collection.
    """

    return build_hook_research_outcome_board(
        producer_hook_search_task=producer_hook_search_task,
        **board_payload,
    )


def run_search_agent(
    *,
    client: NotionClientLike,
    targets: LivePipelineTargets,
    search_targets: list[NativeSourceTarget],
    verified_facts: set[str],
    submitted_at: str,
    writer: WorkflowWriter | None = None,
    analyst: WorkflowAnalyst | None = None,
    knowledge_store: KnowledgeStore | None = None,
    timeout_seconds: float = 30.0,
    fetcher: Fetcher | None = None,
    collected_at: str | None = None,
) -> SearchAgentReport:
    compliance_checks = [assess_target_compliance(target) for target in search_targets]
    allowed_targets = [
        target
        for target, check in zip(search_targets, compliance_checks, strict=True)
        if check.status != "blocked"
    ]
    skipped_target_handles = [
        target.handle
        for target, check in zip(search_targets, compliance_checks, strict=True)
        if check.status == "blocked"
    ]

    items = collect_native_source_items(
        targets=allowed_targets,
        timeout_seconds=timeout_seconds,
        fetcher=fetcher,
        collected_at=collected_at,
    )

    valid_items: list[SourceItem] = []
    evidence_logs: list[EvidenceLogEntry] = []
    dropped_item_ids: list[str] = []
    for item in items:
        try:
            evidence_logs.append(build_evidence_log_entry(item))
        except ValueError:
            dropped_item_ids.append(item.item_id)
            continue
        valid_items.append(item)

    pipeline_results = run_live_pipeline(
        client=client,
        targets=targets,
        items=valid_items,
        verified_facts=verified_facts,
        submitted_at=submitted_at,
        writer=writer,
        analyst=analyst,
        knowledge_store=knowledge_store,
    )
    return SearchAgentReport(
        compliance_checks=compliance_checks,
        evidence_logs=evidence_logs,
        pipeline_results=pipeline_results,
        skipped_target_handles=skipped_target_handles,
        dropped_item_ids=dropped_item_ids,
    )


def assess_target_compliance(target: NativeSourceTarget) -> ComplianceCheck:
    source_url = resolve_target_url(target)
    if not source_url.startswith("https://"):
        return ComplianceCheck(
            target_handle=target.handle,
            platform=target.platform,
            source_url=source_url,
            status="blocked",
            risk_level="high",
            reason="non_https_source",
            collection_mode="do_not_collect",
        )

    if target.platform in {"instagram", "linkedin", "tiktok"}:
        return ComplianceCheck(
            target_handle=target.handle,
            platform=target.platform,
            source_url=source_url,
            status="review",
            risk_level="medium",
            reason="public_page_only_no_auth_or_personal_data",
            collection_mode="public_metadata_only",
        )

    return ComplianceCheck(
        target_handle=target.handle,
        platform=target.platform,
        source_url=source_url,
        status="allowed",
        risk_level="low",
        reason="public_source_minimal_collection",
        collection_mode="public_page_or_feed",
    )


def build_evidence_log_entry(item: SourceItem) -> EvidenceLogEntry:
    source_url = item.source_url.strip()
    timestamp = item.published_at.strip() or item.collected_at.strip()
    raw_excerpt = _excerpt(item.transcript_text)
    if not source_url:
        raise ValueError("source_url is required for evidence log")
    if not timestamp:
        raise ValueError("timestamp is required for evidence log")
    if not raw_excerpt:
        raise ValueError("raw_excerpt is required for evidence log")

    return EvidenceLogEntry(
        item_id=item.item_id,
        source_type=item.source_type,
        route=item.routing_decision,
        source_url=source_url,
        timestamp=timestamp,
        raw_excerpt=raw_excerpt,
        confidence_score=item.routing_confidence,
    )


def _excerpt(text: str, limit: int = 280) -> str:
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"
