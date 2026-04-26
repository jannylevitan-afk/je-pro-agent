import pytest

from content_engine.context.workflow_b_rules import WorkflowBDecision
from content_engine.llm.analyst import AnthropicPipelineAnalyst
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import ContentBrief, IdeaCandidate, InsightCard
from content_engine.services.analyst import AnalystReport, WriterSpec, run_analyst, run_analyst_batch


class StubAnthropicClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses

    def generate_text(self, *, system_prompt, user_prompt, max_tokens, model=None, temperature=None) -> str:
        return self._responses.pop(0)


_INSIGHT_JSON = (
    '{"useful_lesson": "Boutique hotel ROI beats mass-market when structure and operations align.", '
    '"emotional_trigger": "status anxiety around deal quality", '
    '"narrative_type": "market_observation", '
    '"reuse_score": 4, '
    '"topic": "boutique hotel strategy", '
    '"angle": "operator discipline turns design into an asset strategy", '
    '"audience_fit": "developer_investor needs downside protection", '
    '"customer_job": "decide whether a hospitality asset is worth trusting", '
    '"pain_point": "beautiful projects hide weak operating logic", '
    '"trigger_event": "reviewing a new Bali hospitality deal", '
    '"desired_outcome": "avoid buying a polished but weak asset", '
    '"behavioral_trigger": "loss_aversion", '
    '"confidence_score": 0.86}'
)


def test_run_analyst_returns_report(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    assert isinstance(report, AnalystReport)
    assert report.preflight_passed is True
    assert report.risk_flags == []


def test_run_analyst_builds_insight_from_extraction(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    assert isinstance(report.insight, InsightCard)
    assert report.insight.useful_lesson == "Boutique hotel ROI beats mass-market when structure and operations align."
    assert report.insight.emotional_trigger == "status anxiety around deal quality"
    assert report.insight.narrative_type == "market_observation"
    assert report.insight.reuse_score == 4
    assert report.insight.audience == "developer_investor"
    assert report.insight.topic == "boutique hotel strategy"
    assert report.insight.angle == "operator discipline turns design into an asset strategy"
    assert report.insight.audience_fit == "developer_investor needs downside protection"
    assert report.insight.content_theme == "boutique_hotels"
    assert report.insight.content_pillar == "expertise_proof"


def test_run_analyst_returns_two_writer_specs_for_boutique_hotels(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    assert len(report.writer_specs) == 2
    lanes = [spec.decision.platform_lane for spec in report.writer_specs]
    assert "instagram_professional" in lanes
    assert "linkedin_b2b" in lanes


def test_run_analyst_writer_specs_have_correct_types(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    for spec in report.writer_specs:
        assert isinstance(spec, WriterSpec)
        assert isinstance(spec.decision, WorkflowBDecision)
        assert isinstance(spec.idea, IdeaCandidate)
        assert isinstance(spec.brief, ContentBrief)
        assert "## Writer Entity TZ" in spec.writer_tz
        assert "JTBD" in spec.writer_tz
        assert "Pain Point" in spec.writer_tz
        assert "Behavioral Trigger" in spec.writer_tz
        assert spec.brief.analyst_tz == spec.writer_tz


def test_run_analyst_linkedin_spec_has_bilingual_brief(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    linkedin_spec = next(s for s in report.writer_specs if s.decision.platform_lane == "linkedin_b2b")
    assert linkedin_spec.brief.working_language == "ru"
    assert linkedin_spec.brief.publish_language == "en"


def test_run_analyst_preflight_flags_empty_transcript(source_item) -> None:
    empty_item = source_item.model_copy(update={"transcript_text": "  "})
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(empty_item, analyst)

    assert report.preflight_passed is False
    assert any("transcript_text" in flag for flag in report.risk_flags)


def test_run_analyst_preflight_flags_unknown_audience(source_item) -> None:
    unknown_item = source_item.model_copy(update={"audience_segment": "unknown_segment"})
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(unknown_item, analyst)

    assert report.preflight_passed is False
    assert any("audience_segment" in flag for flag in report.risk_flags)


def test_run_analyst_accepts_all_architecture_content_themes(source_item) -> None:
    themes = [
        "founder_journey",
        "expert_pain_bali",
        "land_and_legal",
        "market_reports",
        "bali_travel",
        "global_trends",
        "wellness_architecture",
        "boutique_hotels",
        "marketing_cases",
    ]

    for theme in themes:
        item = source_item.model_copy(update={"content_theme": theme})
        analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

        report = run_analyst(item, analyst)

        assert not any("content_theme" in flag for flag in report.risk_flags)


def test_run_analyst_batch_deduplicates_by_dedupe_key(source_item) -> None:
    duplicate = source_item.model_copy(
        update={
            "item_id": "itm_001_duplicate",
            "routing_confidence": 0.95,
            "engagement_signals": {"views": 50},
        }
    )
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    reports = run_analyst_batch([source_item, duplicate], analyst)

    assert len(reports) == 1
    assert reports[0].source_note.raw_text == duplicate.transcript_text


def test_run_analyst_brief_key_points_use_ai_extracted_lesson(source_item) -> None:
    analyst = AnthropicPipelineAnalyst(StubAnthropicClient(responses=[_INSIGHT_JSON]))

    report = run_analyst(source_item, analyst)

    instagram_spec = next(s for s in report.writer_specs if s.decision.platform_lane == "instagram_professional")
    assert any(
        "Boutique hotel ROI" in point
        for point in instagram_spec.brief.key_points
    )
