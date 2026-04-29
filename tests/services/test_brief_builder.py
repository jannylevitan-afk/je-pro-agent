import pytest

from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import ApprovedOpportunity, ProducerDecision
from content_engine.services.brief_builder import build_brief, build_briefs


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


def make_decision(**overrides: object) -> ProducerDecision:
    payload = {
        "decision_id": "decision_opp_001",
        "opportunity_id": "opp_001",
        "source_item_id": "itm_001",
        "decision": "approve",
        "selected_workflow": "workflow_b",
        "selected_platform": "instagram",
        "priority": "high",
        "production_intent": "Create one source-backed instagram text asset for #недвижка.",
        "season_id": "season_001",
        "episode_id": "episode_001",
        "scene_id": "scene_001",
        "reason": "Strong enough source-backed opportunity.",
        "constraints": ["Do not invent facts.", "Use one selected platform only."],
        "required_evidence": ["source URL", "timestamp", "raw excerpt", "confidence score"],
        "created_at": "2026-04-29T10:00:00+08:00",
    }
    payload.update(overrides)
    return ProducerDecision(**payload)


def make_approved(**overrides: object) -> ApprovedOpportunity:
    payload = {
        "approved_id": "approved_opp_001",
        "decision_id": "decision_opp_001",
        "opportunity_id": "opp_001",
        "source_item_id": "itm_001",
        "selected_workflow": "workflow_b",
        "selected_platform": "instagram",
        "priority": "high",
        "production_intent": "Create one source-backed instagram text asset for #недвижка.",
        "core_idea": "Cheap land can hide expensive structure risk.",
        "jane_adaptation_brief": "Turn this into one concrete #недвижка warning.",
        "evidence_refs": ["https://t.me/BaliLawyer/10"],
        "risk_flags": ["legal_claims_need_source_boundary"],
        "season_id": "season_001",
        "episode_id": "episode_001",
        "scene_id": "scene_001",
        "created_at": "2026-04-29T10:00:00+08:00",
    }
    payload.update(overrides)
    return ApprovedOpportunity(**payload)


def test_build_workflow_b_brief_from_approved_opportunity() -> None:
    result = build_brief(
        approved=make_approved(),
        opportunity=make_opportunity(),
        decision=make_decision(),
        created_at="2026-04-29T10:00:00+08:00",
    )

    brief = result.brief
    assert brief.workflow == "workflow_b"
    assert brief.selected_platform == "instagram"
    assert brief.platform_variants == []
    assert "standalone CTA question" in " ".join(brief.must_not_include)
    assert "source-backed" in brief.production_intent


def test_build_workflow_b_linkedin_brief_sets_english_publish_language() -> None:
    result = build_brief(
        approved=make_approved(selected_platform="linkedin"),
        opportunity=make_opportunity(suggested_platform="linkedin"),
        decision=make_decision(selected_platform="linkedin"),
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert result.brief.workflow == "workflow_b"
    assert result.brief.publish_language == "en"
    assert result.brief.internal_working_language == "ru"


def test_build_workflow_a_brief_keeps_video_fields_and_no_publish_queue() -> None:
    result = build_brief(
        approved=make_approved(
            selected_workflow="workflow_a",
            selected_platform="instagram",
            production_intent="Create one source-backed instagram video asset for #bali life.",
        ),
        opportunity=make_opportunity(
            suggested_workflow="workflow_a",
            source_type="instagram_reel",
            source_url="https://www.instagram.com/reel/example/",
            rubric="#bali life",
            content_theme="bali_travel",
            emotional_trigger="desire",
        ),
        decision=make_decision(
            selected_workflow="workflow_a",
            selected_platform="instagram",
            production_intent="Create one source-backed instagram video asset for #bali life.",
        ),
        created_at="2026-04-29T10:00:00+08:00",
    )

    brief = result.brief
    assert brief.workflow == "workflow_a"
    assert brief.video_refs == ["https://www.instagram.com/reel/example/"]
    assert "publish queue" in " ".join(brief.must_not_include)
    assert not hasattr(brief, "publish_queue")


def test_build_brief_rejects_mismatched_opportunity() -> None:
    with pytest.raises(ValueError, match="opportunity_id"):
        build_brief(
            approved=make_approved(opportunity_id="opp_other"),
            opportunity=make_opportunity(opportunity_id="opp_001"),
            decision=make_decision(opportunity_id="opp_other"),
        )


def test_build_briefs_maps_many_approved_items() -> None:
    approved_items = [
        make_approved(),
        make_approved(
            approved_id="approved_opp_002",
            decision_id="decision_opp_002",
            opportunity_id="opp_002",
            source_item_id="itm_002",
            selected_platform="linkedin",
        ),
    ]
    opportunities = [
        make_opportunity(),
        make_opportunity(
            opportunity_id="opp_002",
            source_item_id="itm_002",
            source_url="https://example.com/2",
            suggested_platform="linkedin",
        ),
    ]
    decisions = [
        make_decision(),
        make_decision(
            decision_id="decision_opp_002",
            opportunity_id="opp_002",
            source_item_id="itm_002",
            selected_platform="linkedin",
        ),
    ]

    results = build_briefs(
        approved_items,
        opportunities=opportunities,
        decisions=decisions,
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert [result.approved_id for result in results] == ["approved_opp_001", "approved_opp_002"]
    assert results[1].brief.selected_platform == "linkedin"
