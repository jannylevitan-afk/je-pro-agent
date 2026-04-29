import pytest

from content_engine.models.content_factory import ContentFactoryRunResult, HumanReviewAsset


def test_human_review_asset_keeps_workflow_b_clean_user_facing_asset() -> None:
    asset = HumanReviewAsset(
        content_id="content_001",
        source_item_id="itm_001",
        opportunity_id="opp_001",
        decision_id="dec_001",
        brief_id="brief_001",
        workflow="workflow_b",
        platform="instagram",
        title="Cheap Bali entry is not the risk",
        pillar="#недвижка",
        audience_segment="developer_investor",
        approval_status="approved_for_human_review",
        final_text="Красивый вход в сделку редко показывает главный риск.",
        internal_ru_master=None,
        selected_hook=None,
        script=None,
        filming_card=None,
        editor_score=0.91,
        revision_notes=[],
        source_refs=["https://t.me/BaliLawyer/10"],
        season_id="season_001",
        episode_id="episode_001",
        scene_id="scene_001",
        created_at="2026-04-29T10:00:00+08:00",
    )

    assert asset.final_text.startswith("Красивый вход")
    assert asset.workflow == "workflow_b"


def test_human_review_asset_rejects_scheduler_or_publisher_fields() -> None:
    with pytest.raises(ValueError, match="Extra inputs"):
        HumanReviewAsset(
            content_id="content_002",
            source_item_id="itm_002",
            opportunity_id="opp_002",
            decision_id="dec_002",
            brief_id="brief_002",
            workflow="workflow_b",
            platform="instagram",
            title="No publisher fields",
            pillar="#experience",
            audience_segment="architect_designer",
            approval_status="approved_for_human_review",
            final_text="Experience is not decor when it changes the business model.",
            editor_score=0.9,
            revision_notes=[],
            source_refs=["https://example.com/source"],
            scheduled_at="2026-05-01T10:00:00+08:00",
        )


def test_content_factory_run_result_uses_active_states_only() -> None:
    result = ContentFactoryRunResult(
        run_id="run_001",
        status="completed",
        started_at="2026-04-29T10:00:00+08:00",
        completed_at="2026-04-29T10:10:00+08:00",
        research_handoff_count=2,
        opportunity_count=2,
        producer_decision_count=2,
        workflow_a_asset_count=1,
        workflow_b_asset_count=1,
        human_review_asset_count=2,
        output_files=["outputs/latest/human_review_assets.json"],
        warnings=[],
    )

    assert result.status == "completed"
