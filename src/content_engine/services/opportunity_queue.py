from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import ApprovedOpportunity, ProducerDecision
from content_engine.services.producer import approve_opportunity, review_opportunities


QueueStatus = Literal["queued", "approved", "hold", "rejected"]


@dataclass(frozen=True, slots=True)
class OpportunityQueueEntry:
    candidate: OpportunityCandidate
    score: float
    status: QueueStatus
    reason: str


@dataclass(frozen=True, slots=True)
class OpportunityQueueResult:
    queued: list[OpportunityQueueEntry]
    decisions: list[ProducerDecision]
    approved: list[ApprovedOpportunity]
    held_ids: list[str]
    rejected_ids: list[str]


def rank_opportunities(candidates: list[OpportunityCandidate]) -> list[OpportunityQueueEntry]:
    """Deduplicate by source item and return highest-value opportunities first."""

    deduped: dict[str, OpportunityCandidate] = {}
    for candidate in candidates:
        existing = deduped.get(candidate.source_item_id)
        if existing is None or _rank_key(candidate) > _rank_key(existing):
            deduped[candidate.source_item_id] = candidate

    ranked = sorted(deduped.values(), key=_rank_key, reverse=True)
    return [
        OpportunityQueueEntry(
            candidate=candidate,
            score=candidate.opportunity_score,
            status="queued",
            reason=_queue_reason(candidate),
        )
        for candidate in ranked
    ]


def process_opportunity_queue(
    candidates: list[OpportunityCandidate],
    *,
    season_id: str,
    episode_id: str,
    scene_id: str,
    created_at: str,
) -> OpportunityQueueResult:
    queued = rank_opportunities(candidates)
    ranked_candidates = [entry.candidate for entry in queued]
    decisions = review_opportunities(
        ranked_candidates,
        season_id=season_id,
        episode_id=episode_id,
        scene_id=scene_id,
        created_at=created_at,
    )
    approved = build_approved_opportunities(
        ranked_candidates,
        decisions,
        created_at=created_at,
    )
    held_ids = [decision.opportunity_id for decision in decisions if decision.decision == "hold"]
    rejected_ids = [decision.opportunity_id for decision in decisions if decision.decision == "reject"]
    return OpportunityQueueResult(
        queued=queued,
        decisions=decisions,
        approved=approved,
        held_ids=held_ids,
        rejected_ids=rejected_ids,
    )


def build_approved_opportunities(
    candidates: list[OpportunityCandidate],
    decisions: list[ProducerDecision],
    *,
    created_at: str,
) -> list[ApprovedOpportunity]:
    candidates_by_id = {candidate.opportunity_id: candidate for candidate in candidates}
    approved: list[ApprovedOpportunity] = []
    for decision in decisions:
        if decision.decision != "approve":
            continue
        candidate = candidates_by_id[decision.opportunity_id]
        approved.append(approve_opportunity(candidate, decision, created_at=created_at))
    return approved


def _rank_key(candidate: OpportunityCandidate) -> tuple[float, float, float, int]:
    return (
        candidate.opportunity_score,
        candidate.evidence_strength_score,
        candidate.strategic_fit_score,
        sum(candidate.public_metrics.values()),
    )


def _queue_reason(candidate: OpportunityCandidate) -> str:
    return (
        f"score={candidate.opportunity_score:.4f}; "
        f"evidence={candidate.evidence_strength_score:.2f}; "
        f"risk={candidate.risk_level}; route={candidate.suggested_workflow}"
    )


__all__ = [
    "OpportunityQueueEntry",
    "OpportunityQueueResult",
    "QueueStatus",
    "build_approved_opportunities",
    "process_opportunity_queue",
    "rank_opportunities",
]
