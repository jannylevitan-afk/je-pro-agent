from __future__ import annotations

import pytest

from content_engine.models.hook_research import HookOpportunity, ProducerHookSearchTask


def make_task_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "directive_id": "hook_rd_001",
        "directive_type": "HOOK_RESEARCH_FOR_WORKFLOW_A",
        "route": "workflow_a",
        "search_goal": "Find source-backed hooks about body energy and discipline fatigue.",
        "season_context": "Month about health, recovery, and softer discipline.",
        "target_audience": "women 28-45, high-functioning founders",
        "core_pain": "I do everything right, but I still have no energy.",
        "core_desire": "Recover energy without violence toward the body.",
        "core_tension": "do more versus restore the system first",
        "target_themes": ["fatigue", "nervous system", "discipline"],
        "forbidden_themes": ["rapid weight loss", "medical diagnosis"],
        "desired_hook_mechanics": ["belief_reversal", "pain_mirror"],
        "platforms": ["Instagram Reels", "TikTok", "YouTube Shorts"],
        "languages_regions": ["RU", "EN"],
        "creator_archetypes": ["wellness creator", "female founder"],
        "date_window": "last_90_days",
        "performance_threshold": "top relative saves/comments/shares",
        "source_count_target": 40,
        "hook_count_target": 8,
        "compliance_boundaries": ["public sources only", "no copying", "no unsupported medical claims"],
        "notes_for_research_agent": "avoid generic biohacking tone",
    }
    payload.update(overrides)
    return payload


def make_hook_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "priority_rank": 1,
        "hook_id": "hook_001",
        "board_id": "hook_board_001",
        "directive_id": "hook_rd_001",
        "opportunity_id": "hook_opp_001",
        "workflow_route": "workflow_a",
        "input_mode": "RESEARCH_MINED",
        "decision_status": "SHORTLISTED",
        "created_at": "2026-05-05T10:00:00+08:00",
        "updated_at": "2026-05-05T10:00:00+08:00",
        "season_id": "season_2026_05_health_villa",
        "monthly_storyline": "Возвращение к телу, энергии и мягкой дисциплине",
        "content_line": "health_identity_energy",
        "episode_id": "ep_02",
        "scene_id": "sc_05",
        "scene_type": "problem_reveal",
        "plot_function": "show_conflict",
        "sales_intensity": "low",
        "producer_topic": "энергия тела и дисциплина",
        "target_audience": "women 28-45, high-functioning founders",
        "core_pain": "I do everything right, but I still have no energy.",
        "core_desire": "Recover energy without violence toward the body.",
        "core_tension": "do more versus restore the system first",
        "desired_cta_direction": "save",
        "source_item_refs": ["src_001"],
        "evidence_refs": ["ev_001"],
        "source_platform": "Instagram",
        "source_type": "public_reel",
        "creator_archetype": "wellness creator",
        "source_recency_days": 12,
        "performance_signal": "high saves and recognition comments",
        "performance_signal_strength": 0.84,
        "relative_baseline_note": "above creator baseline",
        "source_relevance_score": 0.91,
        "source_confidence_score": 0.82,
        "reuse_boundary": "adapt pattern only; do not copy wording, story, creator identity, or visual sequence",
        "hook_mechanic": "belief_reversal",
        "attention_trigger": "recognition",
        "opening_move": "remove self-blame first",
        "visual_hook_type": "direct_to_camera",
        "spoken_hook_type": "statement",
        "narrative_formula": "PAS",
        "emotional_trigger": "recognition",
        "retention_mechanic": "viewer stays to understand why effort is not creating energy",
        "cta_pattern": "save",
        "why_it_performed": "It mirrors a precise pain and reframes it without shame.",
        "adapted_hook_for_jane": "Ты не ленивая. Твоё тело просто больше не верит, что ты в безопасности.",
        "first_frame_text": "Ты не ленивая.",
        "spoken_opening": "Ты не ленивая.",
        "video_angle": "Усталость как защитный режим тела, не провал силы воли.",
        "micro_script_seed": "Jane explains why discipline fails when the body stays in protection mode.",
        "cta_direction": "save",
        "visual_opening_direction": "close-up, calm pause, direct eye contact",
        "tone_direction": "calm, precise, lived expertise",
        "producer_alignment_score": 0.9,
        "audience_pain_match_score": 0.9,
        "hook_strength_score": 0.88,
        "evidence_confidence_score": 0.82,
        "trend_recency_score": 0.8,
        "originality_score": 0.92,
        "execution_ease_score": 0.85,
        "cta_fit_score": 0.8,
        "factual_safety_score": 0.9,
        "risk_penalty": 0.05,
        "final_priority_score": 0.87,
        "risk_level": "low",
        "claim_risk": "low",
        "copy_risk": "low",
        "tone_risk": "low",
        "brand_risk": "low",
        "platform_policy_risk": "low",
        "risk_notes": "Frame as personal/educational, not diagnosis.",
        "required_rewrite": False,
        "qa_status": "PASS",
        "human_decision": "APPROVE_FOR_WORKFLOW_A",
        "reviewer_name": "Producer",
        "reviewed_at": "2026-05-05T11:00:00+08:00",
        "reviewer_notes": "Strong fit for the episode.",
        "next_action": "CREATE_WORKFLOW_A_BRIEF",
    }
    payload.update(overrides)
    return payload


def test_producer_hook_search_task_requires_workflow_a_route() -> None:
    with pytest.raises(ValueError, match="workflow_a"):
        ProducerHookSearchTask(**make_task_payload(route="workflow_b"))


def test_research_mined_hook_requires_source_item_refs() -> None:
    with pytest.raises(ValueError, match="source_item_refs"):
        HookOpportunity(**make_hook_payload(source_item_refs=[]))


def test_research_mined_hook_requires_evidence_refs() -> None:
    with pytest.raises(ValueError, match="evidence_refs"):
        HookOpportunity(**make_hook_payload(evidence_refs=[]))


def test_producer_original_hook_must_not_contain_source_refs() -> None:
    with pytest.raises(ValueError, match="must not contain source/evidence refs"):
        HookOpportunity(
            **make_hook_payload(
                input_mode="PRODUCER_ORIGINAL",
                source_item_refs=["src_001"],
                evidence_refs=[],
                source_platform=None,
                source_type=None,
                creator_archetype=None,
                source_recency_days=None,
                performance_signal=None,
                performance_signal_strength=None,
                source_relevance_score=None,
                source_confidence_score=None,
                producer_original_basis=["SeasonBible", "SceneCard"],
            )
        )


def test_producer_original_hook_requires_strategy_basis() -> None:
    with pytest.raises(ValueError, match="producer_original_basis"):
        HookOpportunity(
            **make_hook_payload(
                input_mode="PRODUCER_ORIGINAL",
                source_item_refs=[],
                evidence_refs=[],
                source_platform=None,
                source_type=None,
                creator_archetype=None,
                source_recency_days=None,
                performance_signal=None,
                performance_signal_strength=None,
                source_relevance_score=None,
                source_confidence_score=None,
                producer_original_basis=[],
            )
        )


def test_high_copy_risk_hook_cannot_be_approved_for_workflow_a() -> None:
    with pytest.raises(ValueError, match="copy-risk"):
        HookOpportunity(**make_hook_payload(copy_risk="high"))


def test_non_pass_hook_cannot_be_approved_for_workflow_a() -> None:
    with pytest.raises(ValueError, match="QA PASS"):
        HookOpportunity(**make_hook_payload(qa_status="NEEDS_REWRITE"))
