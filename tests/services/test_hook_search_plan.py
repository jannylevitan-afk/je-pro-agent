from __future__ import annotations

from content_engine.services.hook_search_plan import build_hook_search_plan
from tests.models.test_hook_research_models import make_task_payload


def test_hook_search_plan_fills_each_producer_rubric_before_moving_on() -> None:
    plan = build_hook_search_plan(make_task_payload())

    assert [batch.topic_key for batch in plan.topic_batches] == [
        "recovery_energy",
        "invisible_quality",
        "bali_real_estate",
        "phygital_villa_experience",
        "founder_ceo_transition",
    ]
    assert all(batch.qualified_target == 10 for batch in plan.topic_batches)
    assert all(batch.stop_condition == "topic_qualified_count >= 10" for batch in plan.topic_batches)
    assert plan.topic_batches[0].order_index == 1
    assert plan.topic_batches[-1].order_index == 5


def test_hook_search_plan_balances_platforms_inside_each_rubric() -> None:
    plan = build_hook_search_plan(make_task_payload())

    assert all(
        batch.platform_targets == {"youtube": 3, "tiktok": 3, "instagram": 4}
        for batch in plan.topic_batches
    )
    assert plan.platform_source_targets == {"youtube": 15, "tiktok": 15, "instagram": 20}


def test_hook_search_plan_searches_russian_and_english_for_every_rubric() -> None:
    plan = build_hook_search_plan(make_task_payload())

    assert plan.language_source_targets == {"ru": 25, "en": 25}
    for batch in plan.topic_batches:
        assert batch.language_targets == {"ru": 5, "en": 5}
        languages = {attempt.language for attempt in batch.search_attempts}
        platforms = {attempt.platform for attempt in batch.search_attempts}
        assert languages == {"ru", "en"}
        assert platforms == {"youtube", "tiktok", "instagram"}
        assert any("рус" in attempt.query_intent.lower() for attempt in batch.search_attempts)
        assert any("english" in attempt.query_intent.lower() for attempt in batch.search_attempts)


def test_hook_search_plan_has_russian_instagram_queries_for_current_season() -> None:
    plan = build_hook_search_plan(make_task_payload())
    instagram_ru_queries = [
        attempt.query
        for batch in plan.topic_batches
        for attempt in batch.search_attempts
        if attempt.platform == "instagram" and attempt.language == "ru"
    ]

    assert instagram_ru_queries
    assert any("site:instagram.com/reel" in query for query in instagram_ru_queries)
    assert any("Бали" in query or "восстановление" in query or "предприниматель" in query for query in instagram_ru_queries)

