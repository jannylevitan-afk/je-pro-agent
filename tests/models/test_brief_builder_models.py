import pytest

from content_engine.models.brief_builder import WorkflowABrief, WorkflowBBrief


def test_workflow_b_brief_keeps_one_selected_platform() -> None:
    brief = WorkflowBBrief(
        brief_id="brief_001",
        source_item_id="itm_001",
        opportunity_id="opp_001",
        decision_id="dec_001",
        workflow="workflow_b",
        selected_platform="instagram",
        rubric="#недвижка",
        audience_segment="developer_investor",
        production_intent="Create one source-backed Instagram post.",
        core_idea="Cheap land can hide legal complexity.",
        angle="The attractive entry price is not the real risk.",
        emotional_trigger="fear",
        source_summary="A public legal channel post performed around land risk.",
        source_text_excerpt="Land structure matters before price.",
        what_performed="Concrete warning with practical stakes.",
        jane_adaptation_instruction="Adapt as Jane's lived expert observation.",
        factual_boundaries=["Do not invent laws or prices."],
        must_include=["one concrete risk", "one Jane-style conclusion"],
        must_not_include=["generic intro", "standalone CTA question"],
        tone_rules=["register_4", "zero generic AI tone"],
        opening_direction="Start with a concrete warning, 5-14 words.",
        quality_criteria=["1 thought / 1 emotion / 1 plot"],
        risk_flags=["legal_claims_need_source_boundary"],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        producer_scene_type="lesson",
        producer_plot_function="teach",
        producer_sales_intensity=1,
        producer_scene_hook="A cheap villa can become an expensive lesson.",
        producer_cta_or_next_hook="Next: the hidden construction question.",
    )

    assert brief.selected_platform == "instagram"
    assert brief.platform_variants == []
    assert brief.producer_scene_type == "lesson"
    assert brief.producer_plot_function == "teach"
    assert brief.producer_sales_intensity == 1
    assert brief.producer_scene_hook == "A cheap villa can become an expensive lesson."
    assert brief.producer_cta_or_next_hook == "Next: the hidden construction question."


def test_brief_rejects_invalid_producer_sales_intensity() -> None:
    with pytest.raises(ValueError, match="producer_sales_intensity"):
        WorkflowBBrief(
            brief_id="brief_001",
            source_item_id="itm_001",
            opportunity_id="opp_001",
            decision_id="dec_001",
            workflow="workflow_b",
            selected_platform="instagram",
            rubric="#недвижка",
            audience_segment="developer_investor",
            production_intent="Create one source-backed Instagram post.",
            core_idea="Cheap land can hide legal complexity.",
            angle="The attractive entry price is not the real risk.",
            emotional_trigger="fear",
            source_summary="A public legal channel post performed around land risk.",
            source_text_excerpt="Land structure matters before price.",
            what_performed="Concrete warning with practical stakes.",
            jane_adaptation_instruction="Adapt as Jane's lived expert observation.",
            factual_boundaries=["Do not invent laws or prices."],
            must_include=["one concrete risk", "one Jane-style conclusion"],
            must_not_include=["generic intro", "standalone CTA question"],
            tone_rules=["register_4", "zero generic AI tone"],
            opening_direction="Start with a concrete warning, 5-14 words.",
            quality_criteria=["1 thought / 1 emotion / 1 plot"],
            risk_flags=[],
            producer_sales_intensity=4,
        )


def test_workflow_b_brief_rejects_platform_variants() -> None:
    with pytest.raises(ValueError, match="platform variants"):
        WorkflowBBrief(
            brief_id="brief_002",
            source_item_id="itm_002",
            opportunity_id="opp_002",
            decision_id="dec_002",
            workflow="workflow_b",
            selected_platform="instagram",
            rubric="#experience",
            audience_segment="architect_designer",
            production_intent="Create one post.",
            core_idea="Wellness design is a commercial signal.",
            angle="Experience as business logic.",
            emotional_trigger="curiosity",
            source_summary="A hotel design article.",
            source_text_excerpt="A short source excerpt.",
            what_performed="Design specificity.",
            jane_adaptation_instruction="Use Jane's product-thinking voice.",
            factual_boundaries=["Do not invent project data."],
            must_include=["one transferable insight"],
            must_not_include=["platform adaptation"],
            tone_rules=["register_6"],
            opening_direction="Start with a source-specific line.",
            quality_criteria=["source-backed"],
            risk_flags=[],
            platform_variants=["linkedin"],
        )


def test_workflow_a_brief_rejects_publish_queue_fields() -> None:
    with pytest.raises(ValueError, match="Extra inputs"):
        WorkflowABrief(
            brief_id="brief_video_001",
            source_item_id="itm_video_001",
            opportunity_id="opp_video_001",
            decision_id="dec_video_001",
            workflow="workflow_a",
            selected_platform="instagram",
            rubric="#bali life",
            audience_segment="lifestyle_expat",
            production_intent="Create a short video script from a high-performing place reel.",
            core_idea="A new Bali place became a social signal.",
            angle="Place as lifestyle proof.",
            emotional_trigger="desire",
            source_summary="A reel about a new Bali place performed well.",
            source_text_excerpt="Opening line from the reel.",
            what_performed="Strong first visual and clear location promise.",
            jane_adaptation_instruction="Use the source hook but make the script Jane-specific.",
            factual_boundaries=["Do not invent location details."],
            must_include=["selected hook", "spoken script", "filming card"],
            must_not_include=["publish queue"],
            tone_rules=["register_2"],
            opening_direction="Keep the first line visual and specific.",
            quality_criteria=["video-native", "source hook preserved when available"],
            risk_flags=[],
            video_refs=["https://www.instagram.com/reel/example/"],
            publish_queue={"status": "ready"},
        )
