from __future__ import annotations

import pytest

from content_engine.models.hook_research import (
    HookOpportunity,
    ProducerHookSearchTask,
    evaluate_video_research_minimums,
)


WORKFLOW_A_TOPIC_TARGETS = {
    "recovery_energy": 10,
    "invisible_quality": 10,
    "bali_real_estate": 10,
    "phygital_villa_experience": 10,
    "founder_ceo_transition": 10,
}


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
        "target_themes": list(WORKFLOW_A_TOPIC_TARGETS),
        "topic_source_targets": WORKFLOW_A_TOPIC_TARGETS,
        "forbidden_themes": ["rapid weight loss", "medical diagnosis"],
        "desired_hook_mechanics": ["belief_reversal", "pain_mirror"],
        "platforms": ["Instagram Reels", "TikTok", "YouTube Shorts"],
        "languages_regions": ["RU", "EN"],
        "creator_archetypes": ["wellness creator", "female founder"],
        "date_window": "last_90_days",
        "performance_threshold": "top relative saves/comments/shares",
        "source_count_target": 50,
        "platform_source_targets": {"youtube": 15, "tiktok": 15, "instagram": 20},
        "short_form_source_count_target": 45,
        "max_long_form_sources": 5,
        "max_short_form_duration_seconds": 180,
        "preferred_aspect_ratio": "9:16",
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
        "source_video_url": "https://www.instagram.com/reel/example/",
        "source_platform": "Instagram",
        "source_type": "public_reel",
        "creator_archetype": "wellness creator",
        "source_recency_days": 12,
        "observed_source_hook": "Internal paraphrase of the source opening.",
        "observed_first_frame_text": "Internal paraphrase of first frame text.",
        "observed_engagement_metrics": {
            "views": 120000,
            "likes": 4300,
            "comments": 310,
            "shares": 520,
            "saves": 740,
        },
        "engagement_score": 14240.0,
        "engagement_rank": 1,
        "scan_batch_size": 50,
        "engagement_selection_reason": "selected as best-performing video by public engagement score",
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


def test_producer_hook_search_task_requires_minimum_50_video_scan_target() -> None:
    with pytest.raises(ValueError, match="source_count_target"):
        ProducerHookSearchTask(**make_task_payload(source_count_target=49))


def test_producer_hook_search_task_requires_workflow_a_platform_mix() -> None:
    with pytest.raises(ValueError, match="platform_source_targets"):
        ProducerHookSearchTask(
            **make_task_payload(
                platform_source_targets={"youtube": 30, "tiktok": 10, "instagram": 10},
            )
        )


def test_producer_hook_search_task_limits_long_form_sources() -> None:
    with pytest.raises(ValueError, match="max_long_form_sources"):
        ProducerHookSearchTask(**make_task_payload(max_long_form_sources=6))


def test_producer_hook_search_task_requires_balanced_topic_targets() -> None:
    with pytest.raises(ValueError, match="topic_source_targets"):
        ProducerHookSearchTask(
            **make_task_payload(
                topic_source_targets={
                    "recovery_energy": 20,
                    "invisible_quality": 10,
                    "bali_real_estate": 10,
                    "phygital_villa_experience": 5,
                    "founder_ceo_transition": 5,
                },
            )
        )


def test_producer_hook_search_task_requires_topic_targets_for_all_themes() -> None:
    with pytest.raises(ValueError, match="topic_source_targets"):
        ProducerHookSearchTask(
            **make_task_payload(
                topic_source_targets={
                    "recovery_energy": 10,
                    "invisible_quality": 10,
                    "bali_real_estate": 10,
                    "phygital_villa_experience": 10,
                    "extra_topic": 10,
                },
            )
        )


def test_producer_hook_search_task_requires_russian_and_english_search_languages() -> None:
    with pytest.raises(ValueError, match="languages_regions"):
        ProducerHookSearchTask(**make_task_payload(languages_regions=["EN"]))


def test_research_mined_hook_requires_source_item_refs() -> None:
    with pytest.raises(ValueError, match="source_item_refs"):
        HookOpportunity(**make_hook_payload(source_item_refs=[]))


def test_research_mined_hook_requires_evidence_refs() -> None:
    with pytest.raises(ValueError, match="evidence_refs"):
        HookOpportunity(**make_hook_payload(evidence_refs=[]))


def test_research_mined_hook_requires_public_video_url() -> None:
    with pytest.raises(ValueError, match="source_video_url"):
        HookOpportunity(**make_hook_payload(source_video_url="internal://source/src_001"))


def test_research_mined_hook_requires_observed_engagement_metrics() -> None:
    with pytest.raises(ValueError, match="observed_engagement_metrics"):
        HookOpportunity(**make_hook_payload(observed_engagement_metrics={}))


def test_video_minimum_gate_keeps_broad_viral_with_real_engagement() -> None:
    decision = evaluate_video_research_minimums(
        {
            "views": 120_000,
            "likes": 3_600,
            "comments": 80,
            "shares": 250,
            "saves": 0,
        }
    )

    assert decision.passes is True
    assert "BROAD_VIRAL" in decision.keep_reasons
    assert decision.like_rate == 3.0


def test_video_minimum_gate_rejects_broad_views_without_discussion_floor() -> None:
    decision = evaluate_video_research_minimums(
        {
            "views": 140_000,
            "likes": 4_200,
            "comments": 20,
            "shares": 0,
            "saves": 0,
        }
    )

    assert decision.passes is False
    assert "BROAD_VIRAL" not in decision.keep_reasons
    assert "BROAD_VIRAL_COMMENTS_BELOW_30" in decision.reject_reasons


def test_video_minimum_gate_requires_like_rate_for_niche_breakout() -> None:
    decision = evaluate_video_research_minimums(
        {
            "views": 30_000,
            "likes": 750,
            "comments": 40,
            "followers": 4_000,
        }
    )

    assert decision.passes is False
    assert "NICHE_VIRAL" not in decision.keep_reasons
    assert "NICHE_LIKE_RATE_BELOW_3_PERCENT" in decision.reject_reasons


def test_video_minimum_gate_rejects_views_without_engagement() -> None:
    decision = evaluate_video_research_minimums(
        {
            "views": 200_000,
            "likes": 900,
            "comments": 8,
            "shares": 0,
            "saves": 0,
        }
    )

    assert decision.passes is False
    assert "LIKE_RATE_BELOW_1_PERCENT" in decision.reject_reasons
    assert "COMMENTS_BELOW_10" in decision.reject_reasons


def test_video_minimum_gate_keeps_small_account_breakout() -> None:
    decision = evaluate_video_research_minimums(
        {
            "views": 18_000,
            "likes": 540,
            "comments": 12,
            "followers": 1_200,
        }
    )

    assert decision.passes is True
    assert "SMALL_ACCOUNT_BREAKOUT" in decision.keep_reasons
    assert decision.views_to_followers_ratio == 15.0


def test_research_mined_hook_requires_minimum_analysis_gate() -> None:
    with pytest.raises(ValueError, match="minimum analysis gate"):
        HookOpportunity(
            **make_hook_payload(
                observed_engagement_metrics={
                    "views": 30_000,
                    "likes": 120,
                    "comments": 5,
                    "shares": 0,
                    "saves": 0,
                },
                engagement_score=720.0,
            )
        )


def test_producer_original_hook_must_not_contain_source_refs() -> None:
    with pytest.raises(ValueError, match="must not contain source/evidence refs"):
        HookOpportunity(
            **make_hook_payload(
                input_mode="PRODUCER_ORIGINAL",
                source_item_refs=["src_001"],
                evidence_refs=[],
                source_video_url=None,
                source_platform=None,
                source_type=None,
                creator_archetype=None,
                source_recency_days=None,
                observed_source_hook=None,
                observed_first_frame_text=None,
                observed_engagement_metrics={},
                engagement_score=None,
                engagement_rank=None,
                scan_batch_size=None,
                engagement_selection_reason=None,
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
                source_video_url=None,
                source_platform=None,
                source_type=None,
                creator_archetype=None,
                source_recency_days=None,
                observed_source_hook=None,
                observed_first_frame_text=None,
                observed_engagement_metrics={},
                engagement_score=None,
                engagement_rank=None,
                scan_batch_size=None,
                engagement_selection_reason=None,
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
