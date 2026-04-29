from content_engine.models.opportunity import OpportunityCandidate
from content_engine.services.opportunity_queue import (
    build_approved_opportunities,
    process_opportunity_queue,
    rank_opportunities,
)


def make_opportunity(**overrides: object) -> OpportunityCandidate:
    payload = {
        "opportunity_id": "opp_001",
        "source_item_id": "itm_001",
        "source_name": "Bali Lawyer",
        "source_type": "telegram_post",
        "source_url": "https://t.me/BaliLawyer/10",
        "topic": "Bali land risk",
        "core_idea": "Cheap land can hide expensive structure risk.",
        "jane_adaptation_brief": "Turn this into one concrete #недвижка warning.",
        "audience_segment": "developer_investor",
        "content_theme": "land_and_legal",
        "rubric": "#недвижка",
        "suggested_workflow": "workflow_b",
        "suggested_platform": "instagram",
        "popularity_label": "high",
        "public_metrics": {"views": 2300, "comments": 12},
        "what_performed": "Concrete legal risk made invisible bureaucracy tangible.",
        "emotional_trigger": "fear",
        "strategic_fit_score": 0.9,
        "evidence_strength_score": 0.8,
        "novelty_score": 0.7,
        "audience_fit_score": 0.9,
        "production_complexity_score": 0.2,
        "risk_level": "medium",
        "risk_flags": ["legal_claims_need_source_boundary"],
        "analyst_reason": "Evidence is concrete and fits the current real estate rubric.",
        "created_at": "2026-04-29T10:00:00+08:00",
    }
    payload.update(overrides)
    return OpportunityCandidate(**payload)


def test_rank_opportunities_dedupes_by_source_and_keeps_highest_score() -> None:
    weak_duplicate = make_opportunity(
        opportunity_id="opp_weak",
        evidence_strength_score=0.4,
        novelty_score=0.3,
    )
    strong_duplicate = make_opportunity(
        opportunity_id="opp_strong",
        evidence_strength_score=0.9,
        novelty_score=0.8,
    )
    other = make_opportunity(
        opportunity_id="opp_other",
        source_item_id="itm_002",
        source_url="https://example.com/2",
        evidence_strength_score=0.7,
        novelty_score=0.6,
    )

    ranked = rank_opportunities([weak_duplicate, other, strong_duplicate])

    assert [entry.candidate.opportunity_id for entry in ranked] == ["opp_strong", "opp_other"]
    assert all(entry.status == "queued" for entry in ranked)


def test_process_opportunity_queue_creates_decisions_and_approved_only_for_approved_items() -> None:
    approved = make_opportunity(opportunity_id="opp_approved")
    held = make_opportunity(
        opportunity_id="opp_held",
        source_item_id="itm_held",
        source_url="https://example.com/held",
        evidence_strength_score=0.35,
    )
    rejected = make_opportunity(
        opportunity_id="opp_rejected",
        source_item_id="itm_rejected",
        source_url="https://example.com/rejected",
        risk_level="high",
        suggested_workflow="drop",
    )

    result = process_opportunity_queue(
        [approved, held, rejected],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert {decision.decision for decision in result.decisions} == {"approve", "hold", "reject"}
    assert [item.opportunity_id for item in result.approved] == ["opp_approved"]
    assert result.held_ids == ["opp_held"]
    assert result.rejected_ids == ["opp_rejected"]


def test_build_approved_opportunities_matches_decisions_by_opportunity_id() -> None:
    result = process_opportunity_queue(
        [make_opportunity()],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    approved = build_approved_opportunities(
        [make_opportunity()],
        result.decisions,
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert approved[0].approved_id == "approved_opp_001"
    assert approved[0].selected_workflow == "workflow_b"
