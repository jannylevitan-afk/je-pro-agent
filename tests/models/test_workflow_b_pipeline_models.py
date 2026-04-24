from content_engine.models.workflow_b import ContentBrief, IdeaCandidate, InsightCard, SourceNote


def test_source_note_keeps_core_metadata() -> None:
    note = SourceNote(
        source_type="telegram_post",
        source_name="@wellstate",
        source_url="https://t.me/wellstate/1",
        date_collected="2026-04-24T08:00:00Z",
        platform="telegram",
        topic_guess="wellness_architecture",
        audience_guess="developer_investor",
        content_type_guess="text",
        engagement_signals={"views": 1200},
        raw_text="Wellness architecture is becoming a luxury differentiator.",
    )

    assert note.platform == "telegram"


def test_content_brief_keeps_linkedin_language_policy() -> None:
    brief = ContentBrief(
        audience="developer_investor",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        funnel_role="authority",
        purpose="Show expertise",
        angle="Wellness architecture as investor signal",
        hook="What luxury buyers now read as trust",
        key_points=["signal", "proof", "market timing"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer replies",
        fact_pack=["verified_public:wellness"],
        source_rigor="expert",
        reference_sources=["https://example.com/report"],
    )

    assert brief.publish_language == "en"
