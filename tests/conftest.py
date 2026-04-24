import pytest

from content_engine.models.approval import DraftRecord
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_a import VideoHook
from content_engine.models.workflow_b import ContentBrief, DraftBundle, InsightCard


@pytest.fixture
def source_item() -> SourceItem:
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
        content_theme="boutique_hotels",
        raw_payload={"text": "Boutique hotel ROI beats mass-market in Bali."},
        transcript_text="Boutique hotel ROI beats mass-market in Bali. Legal structure matters most.",
        media_urls=[],
        engagement_signals={"views": 1200},
        routing_decision="workflow_b",
        routing_reason="textual depth",
        routing_confidence=0.91,
        processing_state="collected",
    )


@pytest.fixture
def video_source_item() -> SourceItem:
    return SourceItem(
        item_id="itm_vid_001",
        source_type="instagram_reel",
        source_name="@clearrealestate",
        source_url="https://instagram.com/reel/1",
        external_item_id="reel_001",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-24T07:45:00Z",
        content_hash="hash_vid_001",
        dedupe_key="instagram:reel_001",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
        raw_payload={"caption": "Cheap villas are never actually cheap."},
        transcript_text="Cheap villas are never actually cheap when legal, design, and management costs arrive.",
        media_urls=["https://cdn.example.com/reel.mp4"],
        engagement_signals={"views": 5200, "saves": 140},
        routing_decision="workflow_a",
        routing_reason="video-native market hook",
        routing_confidence=0.94,
        processing_state="collected",
    )


@pytest.fixture
def insight_card() -> InsightCard:
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


@pytest.fixture
def instagram_brief(insight_card: InsightCard) -> ContentBrief:
    return ContentBrief(
        audience=insight_card.audience,
        platform="instagram",
        platform_lane="instagram_professional",
        working_language="ru",
        publish_language="ru",
        funnel_role="authority",
        purpose="Build credibility with developer audience",
        angle=insight_card.useful_lesson,
        hook="Most hotel listings hide the real numbers.",
        key_points=["ROI", "legal structure", "management quality"],
        cta_type="save",
        tone="register_2",
        length_target="medium",
        engagement_objective="Saves from developers",
        fact_pack=["boutique ROI exceeds mass-market"],
        source_rigor="standard",
        reference_sources=[],
    )


@pytest.fixture
def linkedin_brief(insight_card: InsightCard) -> ContentBrief:
    return ContentBrief(
        audience=insight_card.audience,
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        funnel_role="authority",
        purpose="Establish market expertise",
        angle=insight_card.useful_lesson,
        hook="Most hotel listings hide the real numbers.",
        key_points=["ROI", "legal structure", "management quality"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer replies",
        fact_pack=["boutique ROI exceeds mass-market"],
        source_rigor="expert",
        reference_sources=[
            "https://example.com/report-1",
            "https://example.com/report-2",
            "https://example.com/report-3",
        ],
    )


@pytest.fixture
def instagram_draft_bundle() -> DraftBundle:
    return DraftBundle(
        title="Developer investor — instagram_professional",
        platform="instagram",
        platform_lane="instagram_professional",
        working_language="ru",
        publish_language="ru",
        audience_portrait="developer_investor",
        voice_register="register_2",
        funnel_role="authority",
        draft_text_ru="Большинство листингов скрывают реальные цифры.",
    )


@pytest.fixture
def linkedin_draft_bundle() -> DraftBundle:
    return DraftBundle(
        title="Developer investor — linkedin_b2b",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Большинство листингов скрывают реальные цифры.",
        draft_text_en="Most hotel listings hide the real numbers.",
    )


@pytest.fixture
def linkedin_draft_record() -> DraftRecord:
    return DraftRecord(
        draft_id="dr_001",
        title="Investor trust signals in 2026",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Русская мастер-версия.",
        draft_text_en="English publish version.",
        version=1,
        workflow_stage="ai_edited",
        review_decision="pending",
        ai_edited=True,
        seven_point_test_passed=True,
        factual_safety="clean",
        linked_brief_id="brief_001",
    )


@pytest.fixture
def video_hook(video_source_item: SourceItem) -> VideoHook:
    return VideoHook(
        hook_id="itm_vid_001_hook_1",
        source_item_id=video_source_item.item_id,
        platform="instagram",
        content_theme="boutique_hotels",
        angle="market_warning for developer_investor",
        hook_text="What looks cheap first is often the most expensive later.",
        hook_type="market_warning",
        score=8,
    )
