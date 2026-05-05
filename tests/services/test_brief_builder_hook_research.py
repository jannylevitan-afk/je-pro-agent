from __future__ import annotations

import pytest

from content_engine.models.hook_research import HookOpportunity, HookResearchOutcomeBoard
from content_engine.services.brief_builder import build_workflow_a_briefs_from_hook_board
from content_engine.services.hook_research import build_hook_research_outcome_board
from content_engine.services.workflow_a import run_workflow_a_from_brief
from tests.models.test_hook_research_models import make_hook_payload
from tests.services.test_hook_research import make_board_payload


def test_brief_builder_converts_only_approved_passed_acceptable_hook_to_workflow_a_brief() -> None:
    board = build_hook_research_outcome_board(**make_board_payload())

    results = build_workflow_a_briefs_from_hook_board(board, created_at="2026-05-05T12:00:00+08:00")

    assert len(results) == 1
    brief = results[0].brief
    assert brief.workflow == "workflow_a"
    assert brief.brief_id == "brief_hook_opp_001"
    assert brief.approved_hook_id == "hook_001"
    assert brief.hook_board_id == "hook_board_001"
    assert brief.source_hook == "Ты не ленивая. Твоё тело просто больше не верит, что ты в безопасности."
    assert brief.first_frame_text == "Ты не ленивая."
    assert brief.cta_direction == "save"
    assert "publish queue" in " ".join(brief.must_not_include)
    assert "Workflow A must not perform research." in brief.factual_boundaries


def test_workflow_a_runs_from_hook_research_brief_without_publish_queue() -> None:
    board = build_hook_research_outcome_board(**make_board_payload())
    brief_result = build_workflow_a_briefs_from_hook_board(board, created_at="2026-05-05T12:00:00+08:00")[0]

    video_asset = run_workflow_a_from_brief(brief_result.brief)

    assert video_asset.selected_hook.hook_text.startswith("Ты не ленивая.")
    assert video_asset.script.script_text
    assert video_asset.filming_card.filmed is False
    assert not hasattr(video_asset, "publish_queue")


def test_brief_builder_does_not_convert_backup_hook_from_board() -> None:
    board = build_hook_research_outcome_board(
        **make_board_payload(
            hook_opportunities=[
                make_hook_payload(
                    hook_id="hook_backup",
                    human_decision="BACKUP",
                    decision_status="BACKUP",
                    next_action="MOVE_TO_BACKLOG",
                )
            ]
        )
    )

    results = build_workflow_a_briefs_from_hook_board(board, created_at="2026-05-05T12:00:00+08:00")

    assert results == []


def test_brief_builder_rejects_board_with_invalid_approved_handoff() -> None:
    approved_hook = make_hook_payload()
    board = build_hook_research_outcome_board(**make_board_payload(hook_opportunities=[approved_hook]))
    assert isinstance(board, HookResearchOutcomeBoard)
    tampered = board.model_copy(update={"hook_opportunities": []})

    with pytest.raises(ValueError, match="approved hook"):
        build_workflow_a_briefs_from_hook_board(tampered, created_at="2026-05-05T12:00:00+08:00")


def test_hook_opportunity_model_blocks_unacceptable_approved_risk_before_brief_builder() -> None:
    with pytest.raises(ValueError, match="acceptable risk"):
        HookOpportunity(**make_hook_payload(risk_level="high"))
