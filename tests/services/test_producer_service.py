from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import (
    CreatorProfile,
    MetricsSnapshot,
    ProductOffer,
    ProducerContext,
    ProducerDecision,
    SeasonSeed,
)
from content_engine.services.producer import (
    calculate_direct_sales_ratio,
    create_producer_brief,
    create_research_directives,
    create_scene_cards,
    create_season_bible,
    review_opportunities,
    review_opportunity,
    run_producer_workflow,
    update_from_metrics,
)


def make_context() -> ProducerContext:
    return ProducerContext(
        creator=CreatorProfile(
            name="Jane Levitan",
            role="Founder",
            niche="Bali real estate and lifestyle",
            positioning="Jane turns Bali life, business, and AILLA product thinking into source-backed content.",
            values=["zero bullshit", "source-backed judgment"],
            tone="sharp, warm, lived expertise",
            personal_boundaries=["no private family details without approval"],
            allowed_personal_themes=["Bali life", "founder decisions"],
            forbidden_themes=["private client data"],
            current_life_context="Building a source-backed content season around Bali opportunities.",
        ),
        audience=["developer_investor", "broker"],
        offers=[
            ProductOffer(
                offer_id="offer_001",
                name="AILLA advisory",
                offer_type="service",
                target_audience="developer_investor",
                core_problem="Beautiful Bali assets can hide legal, market, or operating risk.",
                promised_transformation="Make cleaner Bali real estate decisions with product thinking.",
                proof_assets=["source-backed market observations"],
                main_objections=["I can judge the deal from price and visuals"],
                funnel_steps=["attention", "problem_recognition", "trust"],
                cta_options=["DM for review"],
            )
        ],
        current_workflow_state="season_seeded",
        channels=["instagram", "linkedin"],
        constraints=["no auto-publishing", "no invented facts"],
        season_seed=SeasonSeed(
            seed_id="seed_001",
            season_goal="Build a serial about Bali real estate decisions.",
            current_context="Jane is collecting market and founder signals.",
            offer_focus="AILLA advisory",
            rubrics_to_emphasize=["#недвижка", "#заметки фаундера"],
            audience_focus=["developer_investor", "broker"],
            channels=["instagram", "linkedin"],
            constraints=["source-backed only", "manual review"],
            date_range="2 weeks",
            success_metrics=["saves", "qualified DMs"],
        ),
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


def test_create_producer_brief_keeps_strategy_context() -> None:
    brief = create_producer_brief(make_context(), created_at="2026-04-29T10:00:00+08:00")

    assert brief.creator_name == "Jane Levitan"
    assert "developer_investor" in brief.audience_summary
    assert "AILLA advisory" in brief.product_summary
    assert brief.season_goal == "Build a serial about Bali real estate decisions."


def test_run_producer_workflow_creates_season_scenes_and_research_directives() -> None:
    output = run_producer_workflow(make_context(), created_at="2026-04-29T10:00:00+08:00")

    assert output.season.narrative_question
    assert len(output.episodes) == 3
    assert len(output.scenes) == 3
    assert len(output.research_directives) == 3
    assert all(directive.target_agent == "research_agent" for directive in output.research_directives)
    assert all(task.target_agent in {"research_agent", "brief_builder", "editorial_gate", "admin_hub"} for task in output.workflow_tasks)


def test_create_research_directives_preserves_search_boundary() -> None:
    context = make_context()
    brief = create_producer_brief(context, created_at="2026-04-29T10:00:00+08:00")
    season = create_season_bible(brief, context, created_at="2026-04-29T10:00:00+08:00")
    scenes = create_scene_cards(season.episodes, context)

    directives = create_research_directives(season, scenes, context, created_at="2026-04-29T10:00:00+08:00")

    assert {directive.target_agent for directive in directives} == {"research_agent"}
    assert all("source_url" in directive.must_collect for directive in directives)
    assert all("private data" in directive.must_avoid for directive in directives)


def test_direct_sales_ratio_stays_within_default_ratio() -> None:
    output = run_producer_workflow(make_context(), created_at="2026-04-29T10:00:00+08:00")

    assert calculate_direct_sales_ratio(output.scenes) == 0.0


def test_review_opportunity_approves_strong_evidence_with_one_platform() -> None:
    decision = review_opportunity(
        make_opportunity(),
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert decision.decision == "approve"
    assert decision.selected_workflow == "workflow_b"
    assert decision.selected_platform == "instagram"
    assert "source-backed" in decision.production_intent


def test_review_opportunity_holds_incomplete_but_usable_signal() -> None:
    decision = review_opportunity(
        make_opportunity(evidence_strength_score=0.35),
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert decision.decision == "hold"
    assert decision.selected_workflow is None
    assert decision.selected_platform is None


def test_review_opportunity_rejects_high_risk_or_drop_route() -> None:
    decision = review_opportunity(
        make_opportunity(risk_level="high", suggested_workflow="drop"),
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert decision.decision == "reject"


def test_review_opportunities_batches_decisions() -> None:
    decisions = review_opportunities(
        [make_opportunity(), make_opportunity(opportunity_id="opp_002", evidence_strength_score=0.35)],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert [decision.decision for decision in decisions] == ["approve", "hold"]


def test_update_from_metrics_strengthens_hooks_for_low_retention() -> None:
    revision = update_from_metrics(
        season_id="season_001",
        metrics=MetricsSnapshot(story_completion_rate=0.21),
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert "strengthen_hooks" in revision.actions
    assert revision.target_agent == "producer"


def test_update_from_metrics_creates_episode_for_hot_questions() -> None:
    revision = update_from_metrics(
        season_id="season_001",
        metrics=MetricsSnapshot(dm_count=25, top_questions=["Можно ли проверить землю до сделки?"]),
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert "plan_episode_from_audience_questions" in revision.actions


def test_service_exports_producer_decision_type_compatibility() -> None:
    decision = review_opportunity(
        make_opportunity(),
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert isinstance(decision, ProducerDecision)
