from content_engine.models.brief_builder import WorkflowABrief, WorkflowBBrief
from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import CreatorProfile, ProductOffer, ProducerContext, SeasonSeed
from content_engine.services.content_factory import build_human_review_assets, run_content_factory_dry_run


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
            rubrics_to_emphasize=["#недвижка"],
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


def test_run_content_factory_dry_run_connects_producer_queue_briefs_and_assets() -> None:
    result = run_content_factory_dry_run(
        context=make_context(),
        opportunities=[
            make_opportunity(),
            make_opportunity(
                opportunity_id="opp_video",
                source_item_id="itm_video",
                source_type="instagram_reel",
                source_url="https://www.instagram.com/reel/example/",
                suggested_workflow="workflow_a",
                suggested_platform="instagram",
                rubric="#bali life",
                content_theme="bali_travel",
                emotional_trigger="desire",
            ),
            make_opportunity(
                opportunity_id="opp_hold",
                source_item_id="itm_hold",
                source_url="https://example.com/hold",
                evidence_strength_score=0.35,
            ),
        ],
        run_id="run_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert result.run_result.status == "completed"
    assert result.run_result.opportunity_count == 3
    assert result.run_result.producer_decision_count == 3
    assert result.run_result.workflow_a_asset_count == 1
    assert result.run_result.workflow_b_asset_count == 1
    assert len(result.briefs) == 2
    assert len(result.human_review_assets) == 2
    assert result.queue_result.held_ids == ["opp_hold"]


def test_build_human_review_assets_creates_clean_workflow_b_asset() -> None:
    dry_run = run_content_factory_dry_run(
        context=make_context(),
        opportunities=[make_opportunity()],
        run_id="run_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    asset = dry_run.human_review_assets[0]

    assert asset.workflow == "workflow_b"
    assert asset.final_text is not None
    assert asset.final_text.startswith("Draft placeholder:")
    assert asset.selected_hook is None
    assert asset.approval_status == "needs_revision"


def test_build_human_review_assets_creates_video_asset_from_workflow_a_brief() -> None:
    dry_run = run_content_factory_dry_run(
        context=make_context(),
        opportunities=[
            make_opportunity(
                opportunity_id="opp_video",
                source_item_id="itm_video",
                source_type="instagram_reel",
                source_url="https://www.instagram.com/reel/example/",
                suggested_workflow="workflow_a",
                suggested_platform="instagram",
                rubric="#bali life",
                content_theme="bali_travel",
                emotional_trigger="desire",
            )
        ],
        run_id="run_video",
        created_at="2026-04-29T10:00:00+08:00",
    )

    asset = dry_run.human_review_assets[0]

    assert asset.workflow == "workflow_a"
    assert asset.selected_hook is not None
    assert asset.script is not None
    assert asset.filming_card is not None
    assert asset.final_text is None


def test_build_human_review_assets_accepts_explicit_brief_list() -> None:
    dry_run = run_content_factory_dry_run(
        context=make_context(),
        opportunities=[make_opportunity()],
        run_id="run_001",
        created_at="2026-04-29T10:00:00+08:00",
    )
    assets = build_human_review_assets(
        dry_run.briefs,
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert len(assets) == 1
    assert isinstance(dry_run.briefs[0].brief, WorkflowBBrief | WorkflowABrief)
