import pytest

from content_engine.models.opportunity import OpportunityCandidate


def test_opportunity_candidate_calculates_source_backed_score() -> None:
    candidate = OpportunityCandidate(
        opportunity_id="opp_001",
        source_item_id="itm_001",
        source_name="Bali Lawyer",
        source_type="telegram_post",
        source_url="https://t.me/BaliLawyer/10",
        topic="Bali land risk",
        core_idea="A cheap land entry can hide expensive legal complexity.",
        jane_adaptation_brief="Turn the source into one concrete #недвижка warning for developer-investors.",
        audience_segment="developer_investor",
        content_theme="land_and_legal",
        rubric="#недвижка",
        suggested_workflow="workflow_b",
        suggested_platform="instagram",
        popularity_label="high",
        public_metrics={"views": 2300, "comments": 12},
        what_performed="Concrete legal risk made invisible bureaucracy tangible.",
        emotional_trigger="fear",
        strategic_fit_score=0.9,
        evidence_strength_score=0.8,
        novelty_score=0.7,
        audience_fit_score=0.9,
        production_complexity_score=0.2,
        risk_level="medium",
        risk_flags=["legal_claims_need_source_boundary"],
        analyst_reason="Evidence is concrete and fits the current real estate rubric.",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert candidate.opportunity_score == pytest.approx(0.75)


def test_opportunity_candidate_rejects_empty_evidence_url() -> None:
    with pytest.raises(ValueError):
        OpportunityCandidate(
            opportunity_id="opp_002",
            source_item_id="itm_002",
            source_name="Unknown",
            source_type="web",
            source_url="",
            topic="Weak signal",
            core_idea="No evidence.",
            jane_adaptation_brief="Do not use.",
            audience_segment="developer_investor",
            content_theme="market_reports",
            rubric="#недвижка",
            suggested_workflow="drop",
            suggested_platform=None,
            popularity_label="low",
            public_metrics={},
            what_performed="Nothing measurable.",
            emotional_trigger="none",
            strategic_fit_score=0.1,
            evidence_strength_score=0.0,
            novelty_score=0.1,
            audience_fit_score=0.1,
            production_complexity_score=0.1,
            risk_level="high",
            risk_flags=["missing_evidence"],
            analyst_reason="Missing source URL.",
            created_at="2026-04-29T10:00:00+08:00",
        )
