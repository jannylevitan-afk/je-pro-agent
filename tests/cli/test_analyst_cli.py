import json

from content_engine.cli.analyst import (
    AnalystCliConfig,
    build_json_report,
    load_analyst_cli_input,
    main,
    render_markdown_report,
    run_analyst_entity,
)
from content_engine.llm.analyst import InsightExtractionResult


class FakeAnalyst:
    def extract_insight(self, item):
        return InsightExtractionResult(
            topic="boutique hotel operating discipline",
            angle="operating logic protects premium positioning",
            useful_lesson="Boutique hospitality only becomes premium when design, legal structure, and operations work together.",
            emotional_trigger="downside protection",
            audience_fit="developer_investor needs proof that the asset logic is stronger than the brochure",
            narrative_type="market_observation",
            reuse_score=4,
            customer_job="decide whether a Bali hospitality asset deserves trust",
            pain_point="beautiful assets can hide weak operating structure",
            trigger_event="reviewing a new hospitality deal",
            desired_outcome="avoid a polished but fragile investment",
            behavioral_trigger="loss_aversion",
            confidence_score=0.88,
        )


def test_load_analyst_cli_input_accepts_wrapped_source_items(tmp_path, source_item) -> None:
    input_path = tmp_path / "sources.json"
    input_path.write_text(
        json.dumps(
            {
                "source_items": [source_item.model_dump(mode="json")],
                "verified_facts": ["Legal structure matters in Bali hospitality deals."],
            }
        ),
        encoding="utf-8",
    )

    loaded = load_analyst_cli_input(input_path)

    assert loaded.source_items == [source_item]
    assert loaded.verified_facts == {"Legal structure matters in Bali hospitality deals."}


def test_run_analyst_entity_returns_cli_output(source_item) -> None:
    output = run_analyst_entity(
        source_items=[source_item],
        analyst=FakeAnalyst(),
        verified_facts={"Legal structure matters in Bali hospitality deals."},
        config=AnalystCliConfig(model="test-model"),
    )

    assert output.model == "test-model"
    assert output.input_count == 1
    assert len(output.reports) == 1
    assert output.reports[0].insight.topic == "boutique hotel operating discipline"


def test_render_markdown_report_contains_writer_entity_tz(source_item) -> None:
    output = run_analyst_entity(
        source_items=[source_item],
        analyst=FakeAnalyst(),
        verified_facts=set(),
        config=AnalystCliConfig(model="test-model"),
    )

    markdown = render_markdown_report(output)

    assert "# Analyst Entity Report" in markdown
    assert "## Source: itm_001" in markdown
    assert "### Source Note" in markdown
    assert "### Insight Card" in markdown
    assert "### Writer Entity TZ" in markdown
    assert "Notion" not in markdown


def test_build_json_report_is_admin_ready(source_item) -> None:
    output = run_analyst_entity(
        source_items=[source_item],
        analyst=FakeAnalyst(),
        verified_facts=set(),
        config=AnalystCliConfig(model="test-model"),
    )

    payload = build_json_report(output)

    assert payload["entity"] == "analyst"
    assert payload["destination"] == "admin_operating_hub"
    assert payload["notion_enabled"] is False
    assert payload["reports"][0]["source_note"]["source_url"] == source_item.source_url
    assert payload["reports"][0]["writer_specs"][0]["writer_tz"].startswith("## Writer Entity TZ")


def test_main_writes_markdown_and_json_with_injected_analyst(tmp_path, source_item) -> None:
    input_path = tmp_path / "sources.json"
    markdown_path = tmp_path / "analyst.md"
    json_path = tmp_path / "analyst.json"
    input_path.write_text(
        json.dumps([source_item.model_dump(mode="json")]),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--input",
            str(input_path),
            "--output",
            str(markdown_path),
            "--json-output",
            str(json_path),
            "--model",
            "test-model",
        ],
        analyst_factory=lambda config: FakeAnalyst(),
    )

    assert exit_code == 0
    assert "Analyst Entity Report" in markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["model"] == "test-model"
