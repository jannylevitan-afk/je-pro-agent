from __future__ import annotations

from content_engine.models.hook_research import HookResearchBlockedResult, HookResearchOutcomeBoard
from content_engine.orchestration.search_agent import run_hook_research_agent
from content_engine.services.hook_research import (
    build_hook_research_outcome_board,
    calculate_video_engagement_score,
    format_hook_research_outcome_board_markdown,
)
from tests.models.test_hook_research_models import make_hook_payload, make_task_payload


def make_board_payload(**overrides: object) -> dict[str, object]:
    hook = make_hook_payload()
    payload: dict[str, object] = {
        "board_header": {
            "board_id": "hook_board_001",
            "board_type": "HOOK_RESEARCH_OUTCOME_BOARD",
            "workflow_route": "workflow_a",
            "status": "READY_FOR_PRODUCER_REVIEW",
            "season_id": "season_2026_05_health_villa",
            "season_title": "Health Villa / May 2026",
            "monthly_storyline": "Возвращение к телу, энергии и мягкой дисциплине",
            "content_line": "health_identity_energy",
            "episode_id": "ep_02",
            "scene_id": "sc_05",
            "created_at": "2026-05-05T10:30:00+08:00",
            "created_by": "ResearchAgent",
            "human_owner": "Producer",
            "output_language": "ru",
        },
        "producer_hook_search_task": make_task_payload(),
        "research_scope": {
            "search_queries_used": ["fatigue discipline nervous system reels"],
            "platform_filters": ["Instagram Reels", "TikTok"],
            "region_filters": ["global"],
            "language_filters": ["ru", "en"],
            "date_filter": "last_90_days",
            "creator_archetype_filter": ["wellness creator", "female founder"],
            "performance_filter": "top relative saves/comments/shares",
            "topic_inclusion_filter": ["fatigue", "discipline"],
            "topic_exclusion_filter": ["medical diagnosis"],
            "compliance_filter": ["public sources only", "no private data"],
            "search_limitations": ["Instagram saves are inferred when public saves are unavailable."],
        },
        "search_summary": {
            "sources_scanned": 50,
            "raw_candidates_collected": 12,
            "duplicates_removed": 2,
            "candidates_rejected": 7,
            "filtered_hook_opportunities": 3,
            "producer_original_hooks_added": 1,
            "research_mined_hooks_added": 2,
            "top_priority_hooks": 1,
            "risky_or_blocked_candidates": 1,
            "average_evidence_confidence": 0.78,
            "average_producer_alignment": 0.86,
            "rejection_reasons": {"OFF_TOPIC": 3, "COPY_RISK": 1},
        },
        "source_evidence_log": [
            {
                "source_item_id": "src_001",
                "evidence_ref": "ev_001",
                "source_platform": "Instagram",
                "source_type": "public_reel",
                "source_url_or_internal_ref": "https://www.instagram.com/reel/example/",
                "creator_name_or_label": "wellness_creator_01",
                "creator_archetype": "wellness creator",
                "date_detected": "2026-05-05T10:00:00+08:00",
                "content_date": "2026-04-24T10:00:00+08:00",
                "language": "en",
                "region": "global",
                "raw_hook_observed": "[internal paraphrase]",
                "performance_signal_type": "high_saves_relative_to_baseline",
                "performance_signal_notes": "comments show strong self-recognition",
                "evidence_strength": 0.82,
                "relevance_score": 0.91,
                "copy_risk": "low",
                "claim_risk": "low",
                "reuse_boundary": "adapt pattern only; do not copy wording/story/visual sequence",
            }
        ],
        "hook_opportunities": [hook],
        "expanded_hook_cards": [
            {
                "hook_id": "hook_001",
                "priority_rank": 1,
                "input_mode": "RESEARCH_MINED",
                "producer_context_summary": "Fits the health/recovery storyline and scene conflict.",
                "source_signal_summary": "High recognition comments around discipline fatigue.",
                "evidence_refs": ["ev_001"],
                "audience_pain": hook["core_pain"],
                "audience_desire": hook["core_desire"],
                "core_tension": hook["core_tension"],
                "extracted_pattern": "Belief reversal: remove shame before explaining the body state.",
                "why_it_worked": hook["why_it_performed"],
                "adaptation_boundary": hook["reuse_boundary"],
                "jane_adapted_hook": hook["adapted_hook_for_jane"],
                "first_frame_text": hook["first_frame_text"],
                "spoken_opening": hook["spoken_opening"],
                "visual_opening": hook["visual_opening_direction"],
                "short_video_seed": hook["micro_script_seed"],
                "cta_direction": hook["cta_direction"],
                "risk_note": hook["risk_notes"],
                "recommended_decision": "APPROVE_FOR_WORKFLOW_A",
            }
        ],
        "scoring_rubric": {
            "producer_alignment_score": 0.18,
            "audience_pain_match_score": 0.16,
            "hook_strength_score": 0.16,
            "evidence_confidence_score": 0.12,
            "trend_recency_score": 0.10,
            "originality_score": 0.10,
            "execution_ease_score": 0.08,
            "cta_fit_score": 0.05,
            "factual_safety_score": 0.05,
            "risk_penalty": -0.20,
        },
        "approved_for_workflow_a": [],
        "rejected_or_held": [],
        "qa_report": {
            "qa_status": "PASS",
            "producer_task_present": True,
            "search_scope_matches_task": True,
            "research_agent_only_collection": True,
            "source_evidence_present": True,
            "no_raw_source_dump_as_final": True,
            "no_copying": True,
            "factual_boundaries_respected": True,
            "storyline_alignment": True,
            "workflow_boundary_ok": True,
            "decision_rules_enforced": True,
            "qa_notes": ["Ready for producer review."],
        },
        "codex_runtime_notes": ["Board contains hook opportunities only, not scripts or publish queue."],
    }
    payload.update(overrides)
    return payload


def test_hook_research_agent_blocks_without_producer_hook_search_task() -> None:
    result = run_hook_research_agent(producer_hook_search_task=None)

    assert isinstance(result, HookResearchBlockedResult)
    assert result.status == "BLOCKED"
    assert result.blocked_reason == "PRODUCER_HOOK_SEARCH_TASK_MISSING"


def test_hook_research_board_blocks_invalid_task_payload() -> None:
    result = build_hook_research_outcome_board(
        producer_hook_search_task={**make_task_payload(), "route": "workflow_b"},
    )

    assert isinstance(result, HookResearchBlockedResult)
    assert result.status == "BLOCKED"
    assert result.blocked_reason == "PRODUCER_HOOK_SEARCH_TASK_INVALID"


def test_hook_research_board_derives_approved_workflow_a_handoffs() -> None:
    board = build_hook_research_outcome_board(**make_board_payload())

    assert isinstance(board, HookResearchOutcomeBoard)
    assert len(board.approved_for_workflow_a) == 1
    handoff = board.approved_for_workflow_a[0]
    assert handoff.approved_hook_id == "hook_001"
    assert handoff.workflow_a_brief_status == "READY_TO_BUILD"
    assert handoff.selected_hook.startswith("Ты не ленивая.")
    assert handoff.source_context["source_video_url"] == "https://www.instagram.com/reel/example/"
    assert handoff.source_context["observed_engagement_metrics"]["saves"] == 740
    assert handoff.factual_boundaries


def test_hook_research_board_requires_scan_count_to_match_task_target() -> None:
    result = build_hook_research_outcome_board(
        **make_board_payload(
            search_summary={
                **make_board_payload()["search_summary"],
                "sources_scanned": 49,
            }
        )
    )

    assert isinstance(result, HookResearchBlockedResult)
    assert result.blocked_reason == "PRODUCER_HOOK_SEARCH_TASK_INVALID"


def test_hook_research_board_blocks_research_rows_without_public_video_url() -> None:
    result = build_hook_research_outcome_board(
        **make_board_payload(
            hook_opportunities=[make_hook_payload(source_video_url=None)],
        )
    )

    assert isinstance(result, HookResearchBlockedResult)
    assert result.blocked_reason == "PRODUCER_HOOK_SEARCH_TASK_INVALID"


def test_video_engagement_score_weights_comments_saves_and_shares_above_views() -> None:
    score = calculate_video_engagement_score(
        {
            "views": 10000,
            "likes": 100,
            "comments": 20,
            "shares": 10,
            "saves": 5,
        }
    )

    assert score == 455.0


def test_hook_research_board_has_no_downstream_video_or_publish_fields() -> None:
    board = build_hook_research_outcome_board(**make_board_payload())

    dumped = board.model_dump_json() if isinstance(board, HookResearchOutcomeBoard) else board.model_dump_json()

    assert "script_blocks" not in dumped
    assert "filming_card" not in dumped
    assert "publish_date" not in dumped
    assert "scheduler_status" not in dumped
    assert "final_platform_captions" not in dumped
    assert "publish_queue" not in dumped


def test_hook_research_board_markdown_is_readable_not_raw_json() -> None:
    board = build_hook_research_outcome_board(**make_board_payload())

    markdown = format_hook_research_outcome_board_markdown(board)

    assert "# HookResearchOutcomeBoard" in markdown
    assert "## 1. Board Header" in markdown
    assert "## 6. Hook Opportunities" in markdown
    assert "https://www.instagram.com/reel/example/" in markdown
    assert "saves=740" in markdown
    assert "```json" not in markdown
    assert "| Priority | Status | Mode |" in markdown
