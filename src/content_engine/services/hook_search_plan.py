from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from content_engine.models.hook_research import ProducerHookSearchTask
from content_engine.models.hook_search_plan import (
    HookSearchAttempt,
    HookSearchPlan,
    HookTopicSearchBatch,
    SearchLanguage,
    SearchPlatform,
)


PER_TOPIC_PLATFORM_TARGETS: dict[SearchPlatform, int] = {"youtube": 3, "tiktok": 3, "instagram": 4}
PER_TOPIC_LANGUAGE_TARGETS: dict[SearchLanguage, int] = {"ru": 5, "en": 5}
LANGUAGE_SOURCE_TARGETS: dict[SearchLanguage, int] = {"ru": 25, "en": 25}


TOPIC_QUERY_BANK: dict[str, dict[str, list[str]]] = {
    "recovery_energy": {
        "ru": [
            "восстановление после выгорания энергия тело предприниматель",
            "дыхание здоровье усталость перегруз предприниматель",
            "нервная система восстановление энергия рилс",
        ],
        "en": [
            "burnout recovery nervous system founder energy",
            "breathing health reset high achiever burnout",
            "body as system post overload recovery",
        ],
    },
    "invisible_quality": {
        "ru": [
            "плесень влажность дом скрытые дефекты гидроизоляция",
            "плесень в доме влажность вентиляция ремонт",
            "скрытые дефекты строительство гидроизоляция",
        ],
        "en": [
            "mold humidity waterproofing hidden defects",
            "air quality mold inspection home defects",
            "waterproofing failure house inspection",
        ],
    },
    "bali_real_estate": {
        "ru": [
            "Бали вилла покупка ошибки недвижимость",
            "Бали недвижимость due diligence вилла риски",
            "Бали стройка виллы задержки инвестор ошибки",
        ],
        "en": [
            "Bali villa buying mistakes due diligence",
            "Bali real estate villa risks construction delays",
            "Bali property investor mistakes villa",
        ],
    },
    "phygital_villa_experience": {
        "ru": [
            "иммерсивное пространство свадьба вилла событие",
            "фиджитал пространство архитектура опыт событие",
            "вилла для свадьбы необычный опыт бренд мероприятие",
        ],
        "en": [
            "immersive wedding venue architecture experience",
            "phygital space villa event brand experience",
            "luxury ocean villa event venue wedding",
        ],
    },
    "founder_ceo_transition": {
        "ru": [
            "основатель CEO запуск проекта команда закулисье",
            "предприниматель переход новая роль запуск бизнеса",
            "фаундер команда запуск проекта реальность",
        ],
        "en": [
            "founder CEO behind the scenes startup launch",
            "building a team founder reality launch",
            "from operator to creator founder transition",
        ],
    },
}


PLATFORM_QUERY_PREFIX = {
    "youtube": "site:youtube.com/shorts",
    "tiktok": "site:tiktok.com/@",
    "instagram": "site:instagram.com/reel",
}


def build_hook_search_plan(task: ProducerHookSearchTask | Mapping[str, Any]) -> HookSearchPlan:
    """Create the rubric-first search plan used before live hook collection.

    The board validator protects the end of the pipeline. This plan protects the
    beginning: Research Agent must not search broadly and then hope the final
    distribution works. It fills each Producer rubric sequentially, in both RU
    and EN, with a per-topic platform split that sums to the board contract.
    """

    producer_task = task if isinstance(task, ProducerHookSearchTask) else ProducerHookSearchTask(**dict(task))
    topic_batches: list[HookTopicSearchBatch] = []

    for order_index, topic_key in enumerate(producer_task.target_themes, start=1):
        qualified_target = producer_task.topic_source_targets[topic_key]
        attempts = _build_topic_attempts(topic_key)
        topic_batches.append(
            HookTopicSearchBatch(
                topic_key=topic_key,
                order_index=order_index,
                qualified_target=qualified_target,
                platform_targets=PER_TOPIC_PLATFORM_TARGETS,
                language_targets=PER_TOPIC_LANGUAGE_TARGETS,
                stop_condition=f"topic_qualified_count >= {qualified_target}",
                search_attempts=attempts,
            )
        )

    return HookSearchPlan(
        directive_id=producer_task.directive_id,
        source_count_target=producer_task.source_count_target,
        platform_source_targets={
            "youtube": producer_task.platform_source_targets["youtube"],
            "tiktok": producer_task.platform_source_targets["tiktok"],
            "instagram": producer_task.platform_source_targets["instagram"],
        },
        topic_source_targets=producer_task.topic_source_targets,
        language_source_targets=LANGUAGE_SOURCE_TARGETS,
        topic_batches=topic_batches,
        notes_for_research_agent=[
            "Search each topic sequentially until its qualified count is met.",
            "Search both Russian and English public videos.",
            "Do not count discovery-only links, incomplete metrics, or off-format videos as qualified.",
            "Use this plan before building HookResearchOutcomeBoard.",
        ],
    )


def _build_topic_attempts(topic_key: str) -> list[HookSearchAttempt]:
    query_bank = TOPIC_QUERY_BANK.get(topic_key)
    if query_bank is None:
        query_bank = {"ru": [topic_key], "en": [topic_key]}

    attempts: list[HookSearchAttempt] = []
    for language, raw_queries in query_bank.items():
        language_key: SearchLanguage = "ru" if language == "ru" else "en"
        language_label = "русский поиск" if language == "ru" else "English search"
        for platform, prefix in PLATFORM_QUERY_PREFIX.items():
            platform_key: SearchPlatform
            if platform == "youtube":
                platform_key = "youtube"
            elif platform == "tiktok":
                platform_key = "tiktok"
            else:
                platform_key = "instagram"
            for raw_query in raw_queries:
                attempts.append(
                    HookSearchAttempt(
                        topic_key=topic_key,
                        platform=platform_key,
                        language=language_key,
                        query=f"{prefix} {raw_query} reels shorts tiktok",
                        query_intent=f"{language_label}: {topic_key} on {platform}",
                    )
                )
    return attempts


__all__ = [
    "LANGUAGE_SOURCE_TARGETS",
    "PER_TOPIC_LANGUAGE_TARGETS",
    "PER_TOPIC_PLATFORM_TARGETS",
    "TOPIC_QUERY_BANK",
    "build_hook_search_plan",
]
