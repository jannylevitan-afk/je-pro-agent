import pytest
from pydantic import ValidationError

from content_engine.models.workflow_b import ContentBrief, InsightCard
from content_engine.services.draft import build_draft_bundle
from content_engine.services.workflow_b import build_content_brief, build_insight_card


def make_insight() -> InsightCard:
    return InsightCard(
        audience="developer_investor",
        platform="instagram",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type="market_observation",
        priority=2,
        reuse_score=4,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass-market by 3x in Bali.",
    )


def make_instagram_brief() -> ContentBrief:
    insight = make_insight()
    return build_content_brief(
        insight,
        platform="instagram",
        platform_lane="instagram_professional",
        funnel_role="authority",
        purpose="Build credibility",
        hook="Most hotel listings hide the real numbers.",
        key_points=["ROI", "occupancy rate", "management cut"],
        cta_type="save",
        tone="register_2",
        length_target="medium",
        engagement_objective="Saves from developers",
        fact_pack=["boutique ROI exceeds mass-market"],
        source_rigor="standard",
        reference_sources=[],
    )


def make_linkedin_brief() -> ContentBrief:
    insight = make_insight()
    return build_content_brief(
        insight,
        platform="linkedin",
        platform_lane="linkedin_b2b",
        funnel_role="authority",
        purpose="Build credibility",
        hook="Most hotel listings hide the real numbers.",
        key_points=["ROI", "occupancy rate", "management cut"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer replies",
        fact_pack=["boutique ROI exceeds mass-market"],
        source_rigor="expert",
        reference_sources=[
            "https://example.com/r1",
            "https://example.com/r2",
            "https://example.com/r3",
        ],
    )


def test_build_draft_bundle_maps_brief_fields() -> None:
    brief = make_instagram_brief()

    bundle = build_draft_bundle(
        brief,
        draft_text_ru="Большинство листингов скрывают реальные цифры.",
        voice_register="register_2",
        audience_portrait="developer_investor",
    )

    assert bundle.platform == "instagram"
    assert bundle.platform_lane == "instagram_professional"
    assert bundle.funnel_role == "authority"
    assert bundle.working_language == "ru"
    assert bundle.publish_language == "ru"
    assert bundle.draft_text_ru == "Большинство листингов скрывают реальные цифры."
    assert bundle.draft_text_en is None


def test_build_draft_bundle_linkedin_requires_en_version() -> None:
    brief = make_linkedin_brief()

    with pytest.raises(ValidationError):
        build_draft_bundle(
            brief,
            draft_text_ru="Большинство листингов скрывают реальные цифры.",
            voice_register="register_3",
            audience_portrait="developer_investor",
        )


def test_build_draft_bundle_linkedin_passes_with_en_version() -> None:
    brief = make_linkedin_brief()

    bundle = build_draft_bundle(
        brief,
        draft_text_ru="Большинство листингов скрывают реальные цифры.",
        voice_register="register_3",
        audience_portrait="developer_investor",
        draft_text_en="Most hotel listings hide the real numbers.",
    )

    assert bundle.publish_language == "en"
    assert bundle.draft_text_en == "Most hotel listings hide the real numbers."
