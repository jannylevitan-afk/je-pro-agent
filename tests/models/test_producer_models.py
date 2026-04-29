import pytest

from content_engine.models.producer import (
    ApprovedOpportunity,
    EpisodePlan,
    ProducerDecision,
    ProducerQAReport,
    ResearchDirective,
    SceneCard,
    SeasonBible,
    SeasonSeed,
)


def test_scene_card_requires_cta_or_next_hook() -> None:
    with pytest.raises(ValueError, match="CTA or next hook"):
        SceneCard(
            scene_id="scene_001",
            episode_id="episode_001",
            channel="instagram",
            format="post",
            scene_type="lesson",
            plot_function="teach",
            sales_intensity=1,
            hook="Useful content can still fail to sell.",
            context="Jane is planning a season around content as a serial.",
            conflict_or_question="Why does value not move people to action?",
            value_point="The scene needs a story function and a business function.",
        )


def test_direct_offer_scene_requires_proof_bridge_and_cta() -> None:
    with pytest.raises(ValueError, match="direct offer"):
        SceneCard(
            scene_id="scene_002",
            episode_id="episode_001",
            channel="instagram",
            format="post",
            scene_type="direct_offer",
            plot_function="invite_action",
            sales_intensity=3,
            hook="Now the offer finally makes sense.",
            context="The season reached the decision stage.",
            conflict_or_question="What is the safest next step?",
            value_point="The product solves the repeated conflict.",
            cta="Apply now.",
        )


def test_research_directive_keeps_research_agent_as_only_collector() -> None:
    directive = ResearchDirective(
        directive_id="rd_001",
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_003",
        rubric="#недвижка",
        audience_segment="developer_investor",
        content_theme="land_and_legal",
        platform_targets=["instagram", "telegram", "web"],
        approved_source_groups=["expert_pain_bali"],
        search_goal="Find public posts about Bali land/legal risk with strong engagement.",
        must_collect=["source_url", "raw_excerpt", "public_metrics"],
        must_avoid=["private data", "login-only content"],
        evidence_requirements=["source URL", "timestamp", "raw excerpt", "confidence score"],
        priority="high",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert directive.target_agent == "research_agent"


def test_producer_decision_requires_workflow_and_platform_when_approved() -> None:
    with pytest.raises(ValueError, match="selected_workflow"):
        ProducerDecision(
            decision_id="dec_001",
            opportunity_id="opp_001",
            source_item_id="itm_001",
            decision="approve",
            selected_workflow=None,
            selected_platform=None,
            priority="high",
            production_intent="Create one source-backed real estate warning.",
            season_id="season_001",
            episode_id="episode_001",
            scene_id="scene_001",
            reason="Strong evidence.",
            constraints=["no invented legal claims"],
            required_evidence=["source_url"],
            created_at="2026-04-29T10:00:00+08:00",
        )


def test_approved_opportunity_preserves_producer_context() -> None:
    approved = ApprovedOpportunity(
        approved_id="approved_001",
        decision_id="dec_001",
        opportunity_id="opp_001",
        source_item_id="itm_001",
        selected_workflow="workflow_b",
        selected_platform="instagram",
        priority="high",
        production_intent="Create one #недвижка post from source-backed legal risk.",
        core_idea="Cheap land can hide expensive structure risk.",
        jane_adaptation_brief="Write as Jane's lived expert warning, not a legal memo.",
        evidence_refs=["https://t.me/BaliLawyer/10"],
        risk_flags=["legal_claims_need_source_boundary"],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert approved.selected_workflow == "workflow_b"
    assert approved.evidence_refs == ["https://t.me/BaliLawyer/10"]


def test_season_bible_requires_at_least_three_episodes() -> None:
    episode = EpisodePlan(
        episode_id="episode_001",
        season_id="season_001",
        title="Why cheap entry is not cheap",
        day_range="day 1",
        episode_question="What makes a deal look safer than it is?",
        conflict="The attractive price hides operational risk.",
        insight="The first risk is usually structure, not price.",
        sales_function="problem_recognition",
        scene_ids=["scene_001"],
        hook_to_next_episode="Tomorrow we look at the proof before the offer.",
    )

    with pytest.raises(ValueError, match="at least 3 episodes"):
        SeasonBible(
            season_id="season_001",
            title="Bali deal reality",
            duration_days=14,
            season_thesis="Jane shows why Bali opportunities need source-backed judgment.",
            narrative_question="Can you invest without falling for surface beauty?",
            main_conflict="Beautiful assets can hide structural risk.",
            audience_goal="Make cleaner investment decisions.",
            product_role="AILLA/product thinking appears as a safer operating lens.",
            emotional_arc=["curiosity", "recognition", "clarity"],
            sales_arc=["attention", "problem_recognition", "trust"],
            episodes=[episode],
            success_metrics=["saves", "qualified DMs"],
        )


def test_producer_qa_report_blocks_low_ethical_safety() -> None:
    with pytest.raises(ValueError, match="ethical_safety"):
        ProducerQAReport(
            report_id="qa_001",
            target_id="season_001",
            narrative_clarity=9,
            audience_relevance=9,
            sales_integration=9,
            content_variety=8,
            proof_strength=8,
            cta_clarity=8,
            operational_readiness=8,
            ethical_safety=8,
            issues=[],
            revision_notes=[],
            created_at="2026-04-29T10:00:00+08:00",
        )


def test_season_seed_keeps_human_strategy_input() -> None:
    seed = SeasonSeed(
        seed_id="seed_001",
        season_goal="Build a serial around Bali real estate decisions.",
        current_context="Jane is collecting source-backed market signals.",
        offer_focus="AILLA / real estate expertise",
        rubrics_to_emphasize=["#недвижка", "#заметки фаундера"],
        audience_focus=["developer_investor", "broker"],
        channels=["instagram", "linkedin"],
        constraints=["no auto-publishing", "source-backed only"],
        date_range="2 weeks",
        success_metrics=["saves", "qualified DMs"],
    )

    assert seed.rubrics_to_emphasize == ["#недвижка", "#заметки фаундера"]
