"""End-to-end pipeline test.

Exercises the full Content Engine flow:

  SeasonSeed / Strategy Input
    -> Producer Agent
    -> ResearchDirective[]
    -> Opportunity Queue (rank + decide)
    -> Brief Builder (WorkflowA + WorkflowB briefs)
    -> Writer Entity / Workflow A
    -> Human Review Assets
    -> Live Pipeline (Notion sync for text + video items)
"""

from content_engine.models.content_factory import HumanReviewAsset
from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import (
    CreatorProfile,
    ProducerContext,
    ProducerOutput,
    ProductOffer,
    SeasonSeed,
)
from content_engine.orchestration.live_pipeline import (
    LivePipelineTargets,
    process_source_item,
    run_live_pipeline,
)
from content_engine.services.content_factory import run_content_factory_dry_run
from tests.notion.conftest import StubNotionClient

CREATED_AT = "2026-05-07T10:00:00+08:00"


def _make_context() -> ProducerContext:
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
            seed_id="seed_e2e",
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


def _make_text_opportunity(**overrides: object) -> OpportunityCandidate:
    payload = {
        "opportunity_id": "opp_text_e2e",
        "source_item_id": "itm_text_e2e",
        "source_name": "Bali Lawyer",
        "source_type": "telegram_post",
        "source_url": "https://t.me/BaliLawyer/42",
        "topic": "Bali land risk",
        "core_idea": "Cheap land can hide expensive structure risk.",
        "jane_adaptation_brief": "Turn this into one concrete #недвижка warning.",
        "audience_segment": "developer_investor",
        "content_theme": "land_and_legal",
        "rubric": "#недвижка",
        "suggested_workflow": "workflow_b",
        "suggested_platform": "instagram",
        "popularity_label": "high",
        "public_metrics": {"views": 3100, "comments": 18},
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
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return OpportunityCandidate(**payload)


def _make_video_opportunity(**overrides: object) -> OpportunityCandidate:
    payload = {
        "opportunity_id": "opp_video_e2e",
        "source_item_id": "itm_video_e2e",
        "source_name": "ClearRealEstate",
        "source_type": "instagram_reel",
        "source_url": "https://www.instagram.com/reel/e2e_test/",
        "topic": "Villa hidden costs",
        "core_idea": "Cheap villas are never actually cheap.",
        "jane_adaptation_brief": "Show hidden cost structure in video format.",
        "audience_segment": "developer_investor",
        "content_theme": "bali_travel",
        "rubric": "#bali life",
        "suggested_workflow": "workflow_a",
        "suggested_platform": "instagram",
        "popularity_label": "high",
        "public_metrics": {"views": 5200, "saves": 140},
        "what_performed": "Price shock visual drove saves.",
        "emotional_trigger": "desire",
        "strategic_fit_score": 0.85,
        "evidence_strength_score": 0.75,
        "novelty_score": 0.8,
        "audience_fit_score": 0.88,
        "production_complexity_score": 0.4,
        "risk_level": "low",
        "risk_flags": [],
        "analyst_reason": "Strong video hook with visual evidence.",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return OpportunityCandidate(**payload)


def _make_weak_opportunity() -> OpportunityCandidate:
    return _make_text_opportunity(
        opportunity_id="opp_weak_e2e",
        source_item_id="itm_weak_e2e",
        source_url="https://example.com/weak",
        evidence_strength_score=0.35,
    )


# ---------------------------------------------------------------------------
# PART 1: Content Factory dry run — full Producer → Queue → Brief → Asset chain
# ---------------------------------------------------------------------------


class TestContentFactoryEndToEnd:
    """Producer → Opportunity Queue → Brief Builder → Human Review Assets."""

    def test_full_dry_run_produces_both_workflow_assets(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[
                _make_text_opportunity(),
                _make_video_opportunity(),
                _make_weak_opportunity(),
            ],
            run_id="e2e_run_001",
            created_at=CREATED_AT,
        )

        # Pipeline completed
        assert result.run_result.status == "completed"

        # Producer created season structure
        producer = result.producer_output
        assert producer.season is not None
        assert len(producer.episodes) >= 1
        assert len(producer.scenes) >= 1
        assert len(producer.research_directives) >= 1

        # Readable producer output matches season
        assert result.readable_producer_output.title == producer.season.title

        # Opportunity queue processed all 3 candidates
        assert result.run_result.opportunity_count == 3
        assert result.run_result.producer_decision_count == 3

        # Weak opportunity held (low evidence)
        assert "opp_weak_e2e" in result.queue_result.held_ids

        # Two briefs generated (text + video)
        assert len(result.briefs) == 2

        # Two human review assets
        assert len(result.human_review_assets) == 2
        assert result.run_result.workflow_a_asset_count == 1
        assert result.run_result.workflow_b_asset_count == 1

    def test_workflow_b_asset_has_real_content(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[_make_text_opportunity()],
            run_id="e2e_wb",
            created_at=CREATED_AT,
        )

        asset = result.human_review_assets[0]
        assert asset.workflow == "workflow_b"
        assert asset.final_text is not None
        assert len(asset.final_text) > 20
        assert "placeholder" not in asset.final_text.lower()
        assert asset.editor_score > 0.0
        assert any("Writer Entity" in note for note in asset.revision_notes)
        # Workflow B should not produce video artifacts
        assert asset.selected_hook is None
        assert asset.script is None
        assert asset.filming_card is None

    def test_workflow_a_asset_has_video_artifacts(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[_make_video_opportunity()],
            run_id="e2e_wa",
            created_at=CREATED_AT,
        )

        asset = result.human_review_assets[0]
        assert asset.workflow == "workflow_a"
        assert asset.selected_hook is not None
        assert asset.script is not None
        assert asset.filming_card is not None
        assert "placeholder" not in asset.script.lower()
        assert "placeholder" not in asset.filming_card.lower()
        assert asset.editor_score > 0.0
        # Workflow A should not produce text content
        assert asset.final_text is None

    def test_linkedin_asset_includes_ru_master(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[_make_text_opportunity(suggested_platform="linkedin")],
            run_id="e2e_linkedin",
            created_at=CREATED_AT,
        )

        asset = result.human_review_assets[0]
        assert asset.platform == "linkedin"
        assert asset.final_text is not None
        assert asset.internal_ru_master is not None
        # LinkedIn final text should be English (no Cyrillic)
        assert not any("а" <= c.lower() <= "я" or c.lower() == "ё" for c in asset.final_text)

    def test_briefs_carry_producer_scene_metadata(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[_make_text_opportunity(), _make_video_opportunity()],
            run_id="e2e_scenes",
            created_at=CREATED_AT,
        )

        for brief_result in result.briefs:
            assert brief_result.brief.producer_scene_type
            assert brief_result.brief.producer_plot_function

    def test_producer_generates_research_directives_and_workflow_tasks(self) -> None:
        result = run_content_factory_dry_run(
            context=_make_context(),
            opportunities=[_make_text_opportunity()],
            run_id="e2e_directives",
            created_at=CREATED_AT,
        )

        producer = result.producer_output
        assert len(producer.research_directives) >= 1
        assert len(producer.workflow_tasks) >= 1
        # Readable output should include agent tasks
        assert len(result.readable_producer_output.agent_tasks) >= 1


# ---------------------------------------------------------------------------
# PART 2: Live Pipeline — Notion sync for text and video items
# ---------------------------------------------------------------------------


def _make_targets() -> LivePipelineTargets:
    return LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )


class TestLivePipelineEndToEnd:
    """SourceItem → routing → Workflow A/B → Notion sync."""

    def test_text_item_flows_through_workflow_b_to_notion(self, source_item) -> None:
        client = StubNotionClient(
            query_results=[{"results": []}] * 5,
            create_results=[
                {"id": "src_1"},
                {"id": "insight_1"},
                {"id": "idea_1"},
                {"id": "brief_1"},
                {"id": "draft_1"},
                {"id": "event_1"},
                {"id": "idea_2"},
                {"id": "brief_2"},
                {"id": "draft_2"},
                {"id": "event_2"},
            ],
        )

        result = process_source_item(
            client=client,
            targets=_make_targets(),
            item=source_item,
            verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
            submitted_at=CREATED_AT,
        )

        # Routed to Workflow B
        assert result.route == "workflow_b"
        # Source page created
        assert result.source_page_id == "src_1"
        # Insight created
        assert result.insight_page_id == "insight_1"
        # Two platform lanes (instagram_professional + linkedin_b2b)
        assert len(result.idea_page_ids) == 2
        assert len(result.brief_page_ids) == 2
        assert len(result.draft_page_ids) == 2
        assert len(result.event_page_ids) == 2
        # No video artifacts
        assert result.script_page_id is None
        assert result.filming_card_page_id is None

    def test_video_item_flows_through_both_workflows_to_notion(
        self, video_source_item
    ) -> None:
        client = StubNotionClient(
            query_results=[{"results": []}] * 5,
            create_results=[
                {"id": "src_1"},
                {"id": "script_1"},
                {"id": "filming_1"},
                {"id": "insight_1"},
                {"id": "idea_1"},
                {"id": "brief_1"},
                {"id": "draft_1"},
                {"id": "event_1"},
                {"id": "idea_2"},
                {"id": "brief_2"},
                {"id": "draft_2"},
                {"id": "event_2"},
            ],
        )

        result = process_source_item(
            client=client,
            targets=_make_targets(),
            item=video_source_item,
            verified_facts=set(),
            submitted_at=CREATED_AT,
        )

        # Routed to both workflows
        assert result.route == "both"
        # Workflow A artifacts
        assert result.script_page_id == "script_1"
        assert result.filming_card_page_id == "filming_1"
        assert result.video_n8n_envelope is not None
        assert result.video_n8n_envelope["route"] == "script_ready"
        assert result.video_telegram_notification is not None
        # Workflow B artifacts
        assert result.insight_page_id == "insight_1"
        assert len(result.draft_page_ids) == 2

    def test_batch_pipeline_processes_mixed_items(
        self, source_item, video_source_item
    ) -> None:
        client = StubNotionClient(
            query_results=[{"results": []}] * 10,
            create_results=[
                # Text item (workflow_b): src, insight, idea*2, brief*2, draft*2, event*2
                {"id": f"text_{i}"} for i in range(10)
            ] + [
                # Video item (both): src, script, filming, insight, idea*2, brief*2, draft*2, event*2
                {"id": f"video_{i}"} for i in range(12)
            ],
        )

        results = run_live_pipeline(
            client=client,
            targets=_make_targets(),
            items=[source_item, video_source_item],
            verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
            submitted_at=CREATED_AT,
        )

        assert len(results) == 2
        routes = [r.route for r in results]
        assert "workflow_b" in routes
        assert "both" in routes

        # Every result has a source page
        assert all(r.source_page_id is not None for r in results)
        # Every result has draft pages
        assert all(len(r.draft_page_ids) >= 1 for r in results)

    def test_draft_contains_final_content_asset(self, source_item) -> None:
        client = StubNotionClient(
            query_results=[{"results": []}] * 5,
            create_results=[
                {"id": "src_1"},
                {"id": "insight_1"},
                {"id": "idea_1"},
                {"id": "brief_1"},
                {"id": "draft_1"},
                {"id": "event_1"},
                {"id": "idea_2"},
                {"id": "brief_2"},
                {"id": "draft_2"},
                {"id": "event_2"},
            ],
        )

        process_source_item(
            client=client,
            targets=_make_targets(),
            item=source_item,
            verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
            submitted_at=CREATED_AT,
        )

        # First draft should contain a Final Content Asset
        first_draft_props = client.create_calls[4][1]
        final_asset_text = first_draft_props["Final Content Asset"]["rich_text"][0][
            "text"
        ]["content"]
        assert "## Final Content Asset" in final_asset_text
        assert "### Final Text" in final_asset_text

    def test_kmd_knowledge_files_written_for_video_item(
        self, tmp_path, video_source_item
    ) -> None:
        from content_engine.knowledge.kmd import MarkdownKnowledgeStore

        client = StubNotionClient(
            query_results=[{"results": []}] * 5,
            create_results=[
                {"id": f"page_{i}"} for i in range(12)
            ],
        )

        result = process_source_item(
            client=client,
            targets=_make_targets(),
            item=video_source_item,
            verified_facts=set(),
            submitted_at=CREATED_AT,
            knowledge_store=MarkdownKnowledgeStore(tmp_path),
        )

        assert len(result.knowledge_file_paths) == 2
        # KMD files created for both workflow paths
        wf_a_path = tmp_path / "workflow_a" / "developer_investor" / "boutique_hotels" / "itm_vid_001.kmd.md"
        wf_b_path = tmp_path / "workflow_b" / "developer_investor" / "boutique_hotels" / "itm_vid_001.kmd.md"
        assert wf_a_path.exists()
        assert wf_b_path.exists()
