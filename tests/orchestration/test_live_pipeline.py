from content_engine.knowledge.kmd import MarkdownKnowledgeStore
from content_engine.orchestration.live_pipeline import (
    LivePipelineTargets,
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
