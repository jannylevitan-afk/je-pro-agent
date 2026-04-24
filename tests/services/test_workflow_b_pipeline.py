from content_engine.models.source_item import SourceItem
from content_engine.services.workflow_b import (
    build_content_brief,
    build_idea_candidate,
    build_insight_card,
    gate_idea_candidate,
    normalize_source_item,
)


def make_source_item() -> SourceItem:
    return SourceItem(
        item_id="itm_001",
        source_type="telegram_post",
        source_name="@wellstate",
        source_url="https://t.me/wellstate/1",
        external_item_id="1",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-24T07:50:00Z",
        content_hash="hash_001",
        dedupe_key="telegram:1",
        audience_segment="developer_investor",
        content_theme="wellness_architecture",
        raw_payload={"text": "Wellness architecture is becoming a differentiator."},
        transcript_text="Wellness architecture is becoming a differentiator.",
        media_urls=[],
        engagement_signals={"views": 1200},
        routing_decision="workflow_b",
        routing_reason="textual depth",
        routing_confidence=0.91,
        processing_state="collected",
    )


def test_normalize_source_item_preserves_tags() -> None:
    note = normalize_source_item(make_source_item())

    assert note.topic_guess == "wellness_architecture"
    assert note.audience_guess == "developer_investor"


def test_build_insight_card_uses_seed_hints() -> None:
    note = normalize_source_item(make_source_item())

    insight = build_insight_card(
        note,
        emotional_trigger="status anxiety",
        useful_lesson="Wellness design is no longer decorative.",
        narrative_type="market_observation",
        reuse_score=4,
    )

    assert insight.content_theme == "wellness_architecture"
    assert insight.reuse_score == 4


def test_build_idea_candidate_inherits_audience_and_pillar_from_insight() -> None:
    note = normalize_source_item(make_source_item())
    insight = build_insight_card(
        note,
        emotional_trigger="status anxiety",
        useful_lesson="Wellness design is no longer decorative.",
        narrative_type="market_observation",
        reuse_score=4,
    )

    idea = build_idea_candidate(
        insight,
        platform="instagram",
        platform_lane="instagram_professional",
        language_mode="ru",
        funnel_role="authority",
        working_title="What buyers miss when they read a villa listing",
        emotional_hook="Fear of paying for the wrong thing",
        desired_reaction="save",
        suggested_format="carousel",
    )

    assert idea.target_audience == "developer_investor"
    assert idea.content_pillar == "expertise_lifestyle"
    assert idea.useful_point == "Wellness design is no longer decorative."


def test_gate_idea_candidate_checks_four_gates() -> None:
    passed, reasons = gate_idea_candidate(
        {
            "audience_fit": True,
            "has_value": True,
            "has_engagement_trigger": True,
            "platform_lane_fit": True,
        }
    )

    assert passed is True
    assert reasons == []


def test_build_content_brief_sets_linkedin_languages() -> None:
    note = normalize_source_item(make_source_item())
    insight = build_insight_card(
        note,
        emotional_trigger="status anxiety",
        useful_lesson="Wellness design is no longer decorative.",
        narrative_type="market_observation",
        reuse_score=4,
    )

    brief = build_content_brief(
        insight,
        platform="linkedin",
        platform_lane="linkedin_b2b",
        funnel_role="authority",
        purpose="Show expertise",
        hook="Luxury buyers now read wellness as signal",
        key_points=["signal", "proof", "market timing"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer replies",
        fact_pack=["verified_public:wellness"],
        source_rigor="expert",
        reference_sources=[
            "https://example.com/report-1",
            "https://example.com/report-2",
            "https://example.com/report-3",
        ],
    )

    assert brief.working_language == "ru"
    assert brief.publish_language == "en"


def test_build_content_brief_requires_three_sources_for_expert_rigor() -> None:
    note = normalize_source_item(make_source_item())
    insight = build_insight_card(
        note,
        emotional_trigger="status anxiety",
        useful_lesson="Wellness design is no longer decorative.",
        narrative_type="market_observation",
        reuse_score=4,
    )

    try:
        build_content_brief(
            insight,
            platform="linkedin",
            platform_lane="linkedin_b2b",
            funnel_role="authority",
            purpose="Show expertise",
            hook="Luxury buyers now read wellness as signal",
            key_points=["signal", "proof", "market timing"],
            cta_type="comment",
            tone="register_3",
            length_target="medium",
            engagement_objective="Developer replies",
            fact_pack=["verified_public:wellness"],
            source_rigor="expert",
            reference_sources=["https://example.com/report-1"],
        )
    except ValueError as exc:
        assert "3" in str(exc)
    else:
        raise AssertionError("Expected expert brief to require at least 3 reference sources")
