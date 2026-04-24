from content_engine.context.workflow_b_rules import (
    WorkflowBDecision,
    expand_workflow_b_decisions,
    infer_narrative_type,
    infer_useful_lesson,
)
from content_engine.models.source_item import SourceItem


def make_source_item(
    *,
    audience_segment: str = "developer_investor",
    content_theme: str = "boutique_hotels",
    transcript_text: str = "Boutique hotel ROI beats mass market when legal structure and operations align.",
    media_urls: list[str] | None = None,
) -> SourceItem:
    return SourceItem(
        item_id="itm_001",
        source_type="telegram_post",
        source_name="@clearvisionary",
        source_url="https://t.me/clearvisionary/1",
        external_item_id="1",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-24T07:55:00Z",
        content_hash="hash_001",
        dedupe_key="telegram:1",
        audience_segment=audience_segment,
        content_theme=content_theme,
        raw_payload={"text": transcript_text},
        transcript_text=transcript_text,
        media_urls=media_urls or [],
        engagement_signals={"views": 1200, "saves": 45},
        routing_decision="workflow_b",
        routing_reason="textual depth",
        routing_confidence=0.91,
        processing_state="collected",
    )


def test_boutique_hotel_theme_expands_to_professional_and_linkedin() -> None:
    decisions = expand_workflow_b_decisions(make_source_item())

    lanes = [decision.platform_lane for decision in decisions]
    assert lanes == ["instagram_professional", "linkedin_b2b"]
    assert decisions[0].tone == "register_3"
    assert decisions[0].funnel_role == "authority"
    assert decisions[1].source_rigor == "expert"


def test_wellness_architecture_spreads_across_both_instagram_lanes_and_linkedin() -> None:
    decisions = expand_workflow_b_decisions(
        make_source_item(
            content_theme="wellness_architecture",
            audience_segment="lifestyle_expat",
        )
    )

    lanes = [decision.platform_lane for decision in decisions]
    assert lanes == [
        "instagram_lifestyle",
        "instagram_professional",
        "linkedin_b2b",
    ]
    assert decisions[0].tone == "register_2"
    assert decisions[2].tone == "register_6"


def test_marketing_cases_get_market_critical_linkedin_rigor() -> None:
    decisions = expand_workflow_b_decisions(
        make_source_item(content_theme="marketing_cases")
    )

    linkedin = next(decision for decision in decisions if decision.platform_lane == "linkedin_b2b")
    assert linkedin.source_rigor == "market-critical"
    assert linkedin.cta_type == "comment"


def test_infer_narrative_type_prefers_bts_for_visual_material() -> None:
    item = make_source_item(
        content_theme="wellness_architecture",
        transcript_text="We walked the site at sunrise and changed the flow after one conversation.",
        media_urls=["https://cdn.example.com/reel.mp4"],
    )

    assert infer_narrative_type(item) == "behind the scenes"


def test_infer_useful_lesson_trims_first_sentence() -> None:
    item = make_source_item(
        transcript_text="Cheap villas are rarely cheap after legal clean-up. The spreadsheet usually lies at first glance.",
    )

    assert infer_useful_lesson(item) == "Cheap villas are rarely cheap after legal clean-up."


def test_decisions_return_structured_records() -> None:
    decisions = expand_workflow_b_decisions(make_source_item())

    assert all(isinstance(decision, WorkflowBDecision) for decision in decisions)
