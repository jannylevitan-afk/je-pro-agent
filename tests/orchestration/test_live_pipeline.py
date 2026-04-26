from content_engine.knowledge.kmd import MarkdownKnowledgeStore
from content_engine.orchestration.live_pipeline import (
    LivePipelineTargets,
    _matching_fact_pack,
    process_source_item,
    run_collector_cycle,
    run_live_pipeline,
)
from tests.notion.conftest import StubNotionClient


def test_process_source_item_routes_text_item_into_workflow_b(source_item) -> None:
    client = StubNotionClient(
        query_results=[
            {"results": []},  # source upsert
            {"results": []},  # brief upsert lane 1
            {"results": []},  # draft upsert lane 1
            {"results": []},  # brief upsert lane 2
            {"results": []},  # draft upsert lane 2
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    result = process_source_item(
        client=client,
        targets=targets,
        item=source_item,
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert result.route == "workflow_b"
    assert result.source_page_id == "src_page_1"
    assert result.insight_page_id == "insight_page_1"
    assert result.script_page_id is None
    assert len(result.idea_page_ids) == 2
    assert len(result.brief_page_ids) == 2
    assert len(result.draft_page_ids) == 2
    assert len(result.event_page_ids) == 2

    first_draft = client.create_calls[4][1]
    final_asset = first_draft["Final Content Asset"]["rich_text"][0]["text"]["content"]
    assert "## Final Content Asset" in final_asset
    assert "**Content ID:** content_draft_itm_001_instagram_professional" in final_asset
    assert "### Final Text" in final_asset
    assert "### Hook" not in final_asset
    assert "### CTA" not in final_asset
    assert "### Traceability" not in final_asset
    assert "### QA" not in final_asset
    assert "- Source IDs: itm_001" not in final_asset
    assert "- Insight ID: insight_page_1" not in final_asset
    assert "- Idea ID: idea_page_1" not in final_asset
    assert "- Brief ID: brief_itm_001_instagram_professional" not in final_asset
    assert "- Draft ID: draft_itm_001_instagram_professional" not in final_asset
    assert "- Edit Version ID: draft_itm_001_instagram_professional_edit_v1" not in final_asset
    assert "Video Hooks" not in final_asset


def test_process_source_item_uses_analyst_for_workflow_b_phase_1_and_2(source_item) -> None:
    class FakeAnalyst:
        def extract_insight(self, item):
            class Result:
                useful_lesson = "Analyst extracted lesson for Writer Entity TZ."
                emotional_trigger = "status anxiety around weak deal logic"
                narrative_type = "market_observation"
                reuse_score = 5
                topic = "analyst topic"
                angle = "analyst angle"
                audience_fit = "developer_investor fit"
                customer_job = "decide whether this deal deserves trust"
                pain_point = "surface story hides weak structure"
                trigger_event = "reviewing a Bali opportunity"
                desired_outcome = "avoid the wrong deal"
                behavioral_trigger = "loss_aversion"
                confidence_score = 0.9

            return Result()

    client = StubNotionClient(
        query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    process_source_item(
        client=client,
        targets=targets,
        item=source_item,
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
        analyst=FakeAnalyst(),
    )

    insight_properties = client.create_calls[1][1]
    assert insight_properties["Angle"]["rich_text"][0]["text"]["content"] == (
        "Analyst extracted lesson for Writer Entity TZ."
    )
    first_brief = client.create_calls[3][1]
    reference_sources = first_brief["Reference sources"]["rich_text"][0]["text"]["content"]
    assert "https://t.me/wellstate/1#source" in reference_sources


def test_matching_fact_pack_ignores_generic_villa_bali_overlap(source_item) -> None:
    item = source_item.model_copy(
        update={
            "transcript_text": "This Bali villa looks beautiful, but the source does not mention AILLA.",
        }
    )

    facts = {
        "AILLA Villa is the flagship experience-development project in Bali.",
        "Front-loaded payment schemes in Bali real estate carry higher buyer risk than milestone-based structures.",
    }

    assert _matching_fact_pack(item, facts) == []


def test_process_source_item_routes_video_item_into_both_workflows(video_source_item) -> None:
    client = StubNotionClient(
        query_results=[
            {"results": []},  # source upsert
            {"results": []},  # brief upsert lane 1
            {"results": []},  # draft upsert lane 1
            {"results": []},  # brief upsert lane 2
            {"results": []},  # draft upsert lane 2
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    result = process_source_item(
        client=client,
        targets=targets,
        item=video_source_item,
        verified_facts=set(),
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert result.route == "both"
    assert result.script_page_id == "script_page_1"
    assert result.filming_card_page_id == "filming_page_1"
    assert client.create_calls[1][1]["Title"]["title"][0]["text"]["content"] == "What cheap villas hide"
    assert result.video_n8n_envelope["route"] == "script_ready"
    assert result.video_telegram_notification["channel"] == "telegram"
    assert "priority 1" in result.video_telegram_notification["message"]
    assert result.insight_page_id == "insight_page_1"
    assert len(result.draft_page_ids) == 2


def test_process_source_item_writes_kmd_material_before_workflow_steps(tmp_path, video_source_item) -> None:
    client = StubNotionClient(
        query_results=[
            {"results": []},  # source upsert
            {"results": []},  # brief upsert lane 1
            {"results": []},  # draft upsert lane 1
            {"results": []},  # brief upsert lane 2
            {"results": []},  # draft upsert lane 2
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    result = process_source_item(
        client=client,
        targets=targets,
        item=video_source_item,
        verified_facts=set(),
        submitted_at="2026-04-24T10:00:00Z",
        knowledge_store=MarkdownKnowledgeStore(tmp_path),
    )

    assert len(result.knowledge_file_paths) == 2
    assert (tmp_path / "workflow_a" / "developer_investor" / "boutique_hotels" / "itm_vid_001.kmd.md").exists()
    assert (tmp_path / "workflow_b" / "developer_investor" / "boutique_hotels" / "itm_vid_001.kmd.md").exists()


def test_run_live_pipeline_processes_batch(source_item, video_source_item) -> None:
    client = StubNotionClient(
        query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
            {"id": "src_page_2"},
            {"id": "script_page_2"},
            {"id": "filming_page_2"},
            {"id": "insight_page_2"},
            {"id": "idea_page_3"},
            {"id": "brief_page_3"},
            {"id": "draft_page_3"},
            {"id": "event_page_3"},
            {"id": "idea_page_4"},
            {"id": "brief_page_4"},
            {"id": "draft_page_4"},
            {"id": "event_page_4"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    results = run_live_pipeline(
        client=client,
        targets=targets,
        items=[source_item, video_source_item],
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert len(results) == 2
    assert [result.route for result in results] == ["workflow_b", "both"]


def test_run_collector_cycle_uses_external_collector(source_item) -> None:
    class FakeCollector:
        def collect(self) -> list:
            return [source_item]

    client = StubNotionClient(
        query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    results = run_collector_cycle(
        collector=FakeCollector(),
        client=client,
        targets=targets,
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert len(results) == 1
    assert results[0].source_item_id == source_item.item_id


def test_process_source_item_uses_injected_writer_for_script_and_draft(
    video_source_item,
) -> None:
    class FakeWriter:
        def write_video_script(
            self,
            *,
            item,
            title: str,
            hook: str,
            body_points: list[str],
            cta: str,
        ) -> str:
            return "Anthropic video script"

        def write_workflow_b_draft(
            self,
            *,
            item,
            insight,
            decision,
            brief,
        ):
            class Draft:
                draft_text_ru = "Anthropic Russian draft"
                draft_text_en = "Anthropic English draft"

            return Draft()

    client = StubNotionClient(
        query_results=[
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
            {"results": []},
        ],
        create_results=[
            {"id": "src_page_1"},
            {"id": "script_page_1"},
            {"id": "filming_page_1"},
            {"id": "insight_page_1"},
            {"id": "idea_page_1"},
            {"id": "brief_page_1"},
            {"id": "draft_page_1"},
            {"id": "event_page_1"},
            {"id": "idea_page_2"},
            {"id": "brief_page_2"},
            {"id": "draft_page_2"},
            {"id": "event_page_2"},
        ],
    )
    targets = LivePipelineTargets(
        sources_database_id="db_sources",
        insights_database_id="db_insights",
        ideas_database_id="db_ideas",
        briefs_database_id="db_briefs",
        drafts_database_id="db_drafts",
        events_database_id="db_events",
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    process_source_item(
        client=client,
        targets=targets,
        item=video_source_item,
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
        writer=FakeWriter(),
    )

    assert client.create_calls[1][1]["Script text"]["rich_text"][0]["text"]["content"] == "Anthropic video script"
    assert client.create_calls[6][1]["Draft text RU"]["rich_text"][0]["text"]["content"] == "Anthropic Russian draft"
    assert client.create_calls[6][1]["Draft text EN"]["rich_text"][0]["text"]["content"] == "Anthropic English draft"
    instagram_final_asset = client.create_calls[6][1]["Final Content Asset"]["rich_text"][0]["text"]["content"]
    linkedin_final_asset = client.create_calls[10][1]["Final Content Asset"]["rich_text"][0]["text"]["content"]
    assert "Anthropic Russian draft" in instagram_final_asset
    assert "Anthropic English draft" in linkedin_final_asset
    assert "Anthropic Russian draft" not in linkedin_final_asset
    assert "### Hook" not in instagram_final_asset
    assert "### CTA" not in instagram_final_asset
    assert "### Traceability" not in instagram_final_asset
    assert "### QA" not in instagram_final_asset
    assert "### Hook" not in linkedin_final_asset
    assert "### CTA" not in linkedin_final_asset
    assert "### Traceability" not in linkedin_final_asset
    assert "### QA" not in linkedin_final_asset
