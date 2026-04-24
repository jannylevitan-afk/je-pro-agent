from content_engine.runtime.dry_run import InMemoryNotionClient, run_local_pipeline_dry_run
from content_engine.runtime.live_run import StaticSourceCollector


class FakeWriter:
    def write_video_script(self, *, item, title: str, hook: str, body_points: list[str], cta: str) -> str:
        return "Anthropic video script"

    def write_workflow_b_draft(self, *, item, insight, decision, brief):
        class Draft:
            draft_text_ru = "Anthropic Russian draft"
            draft_text_en = "Anthropic English draft" if decision.platform_lane == "linkedin_b2b" else None

        return Draft()


def test_in_memory_notion_client_supports_upsert_queries() -> None:
    client = InMemoryNotionClient()

    created = client.create_database_page(
        "db_sources",
        {
            "Dedupe key": {
                "rich_text": [{"type": "text", "text": {"content": "telegram:1"}}]
            }
        },
    )

    response = client.query_database(
        "db_sources",
        {
            "filter": {
                "property": "Dedupe key",
                "rich_text": {"equals": "telegram:1"},
            }
        },
    )

    assert created["id"].startswith("db_sources_page_")
    assert response["results"][0]["id"] == created["id"]


def test_run_local_pipeline_dry_run_returns_both_workflow_outputs(source_item, video_source_item) -> None:
    report = run_local_pipeline_dry_run(
        collector=StaticSourceCollector([source_item, video_source_item]),
        writer=FakeWriter(),
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert len(report.item_results) == 2
    assert report.item_results[0].route == "workflow_b"
    assert report.item_results[1].route == "both"
    assert len(report.database_snapshots["scripts"]) == 1
    assert len(report.database_snapshots["drafts"]) == 4
    assert report.database_snapshots["scripts"][0]["Script text"] == "Anthropic video script"
    assert any(
        row["Draft text EN"] == "Anthropic English draft"
        for row in report.database_snapshots["drafts"]
    )
