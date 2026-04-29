from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from content_engine.models.opportunity import OpportunityCandidate
from content_engine.models.producer import (
    ApprovedOpportunity,
    EpisodePlan,
    MetricsSnapshot,
    ProducerBrief,
    ProducerContext,
    ProducerDecision,
    ProducerOutput,
    ProducerQAReport,
    ResearchDirective,
    SceneCard,
    SeasonBible,
    WorkflowTask,
)


ProducerTargetAgent = Literal["producer"]

_DEFAULT_CREATED_AT = "2026-04-29T00:00:00+08:00"
_ACTIVE_TASK_TARGETS = ("research_agent", "brief_builder", "editorial_gate", "admin_hub")
_DIRECT_RESEARCH_FIELDS = ["source_url", "timestamp", "raw_excerpt", "public_metrics", "confidence_score"]
_DIRECT_RESEARCH_AVOID = ["private data", "login-only content", "closed community material"]
_EVIDENCE_REQUIREMENTS = ["source URL", "timestamp", "raw excerpt", "confidence score"]


@dataclass(frozen=True, slots=True)
class ProducerRevision:
    season_id: str
    target_agent: ProducerTargetAgent
    actions: list[str]
    reason: str
    created_at: str


def run_producer_workflow(
    context: ProducerContext,
    *,
    created_at: str = _DEFAULT_CREATED_AT,
) -> ProducerOutput:
    brief = create_producer_brief(context, created_at=created_at)
    season = create_season_bible(brief, context, created_at=created_at)
    scenes = create_scene_cards(season.episodes, context)
    directives = create_research_directives(season, scenes, context, created_at=created_at)
    qa_report = qa_producer_plan(
        brief=brief,
        season=season,
        episodes=season.episodes,
        scenes=scenes,
        created_at=created_at,
    )
    tasks = create_workflow_tasks(
        research_directives=directives,
        scenes=scenes,
        created_at=created_at,
    )
    return ProducerOutput(
        brief=brief,
        season=season,
        episodes=season.episodes,
        scenes=scenes,
        research_directives=directives,
        workflow_tasks=tasks,
        qa_report=qa_report,
        memory=context.memory,
    )


def create_producer_brief(
    context: ProducerContext,
    *,
    created_at: str = _DEFAULT_CREATED_AT,
) -> ProducerBrief:
    seed = context.season_seed
    return ProducerBrief(
        brief_id=f"producer_brief_{seed.seed_id}",
        creator_name=context.creator.name,
        audience_summary=_join_unique([*context.audience, *seed.audience_focus]),
        product_summary=_product_summary(context),
        season_goal=seed.season_goal,
        constraints=_unique([*context.constraints, *seed.constraints]),
        channels=_unique([*context.channels, *seed.channels]),
        metrics=seed.success_metrics,
    )


def create_season_bible(
    brief: ProducerBrief,
    context: ProducerContext,
    *,
    created_at: str = _DEFAULT_CREATED_AT,
) -> SeasonBible:
    season_id = f"season_{context.season_seed.seed_id}"
    episodes = plan_episodes(season_id=season_id, brief=brief, context=context)
    return SeasonBible(
        season_id=season_id,
        title=_season_title(context),
        duration_days=_duration_days(context.season_seed.date_range),
        season_thesis=_season_thesis(brief, context),
        narrative_question=_narrative_question(context),
        main_conflict=_main_conflict(context),
        audience_goal=_audience_goal(context),
        product_role=_product_role(context),
        emotional_arc=["curiosity", "recognition", "clarity"],
        sales_arc=["attention", "problem_recognition", "trust"],
        episodes=episodes,
        success_metrics=context.season_seed.success_metrics,
    )


def plan_episodes(
    *,
    season_id: str,
    brief: ProducerBrief,
    context: ProducerContext,
) -> list[EpisodePlan]:
    audience_goal = _audience_goal(context)
    conflict = _main_conflict(context)
    return [
        EpisodePlan(
            episode_id=f"{season_id}_episode_1",
            season_id=season_id,
            title="Контекст сезона",
            day_range="day 1-2",
            episode_question="Почему эта тема сейчас должна удержать внимание?",
            conflict=conflict,
            insight="Сначала продаётся идея и путь, а не продукт.",
            sales_function="awareness",
            scene_ids=[f"{season_id}_scene_1"],
            hook_to_next_episode="Дальше покажем, где аудитория узнаёт свой риск.",
        ),
        EpisodePlan(
            episode_id=f"{season_id}_episode_2",
            season_id=season_id,
            title="Проблема и узнавание",
            day_range="day 3-5",
            episode_question=f"Что мешает аудитории получить: {audience_goal}?",
            conflict=conflict,
            insight="Проблема должна стать видимой через конкретную сцену или источник.",
            sales_function="problem_recognition",
            scene_ids=[f"{season_id}_scene_2"],
            hook_to_next_episode="Дальше добавим доказательства и доверие.",
        ),
        EpisodePlan(
            episode_id=f"{season_id}_episode_3",
            season_id=season_id,
            title="Доверие и доказательство",
            day_range="day 6-7",
            episode_question="Как доказать мысль без фейковых кейсов и давления?",
            conflict=conflict,
            insight="Proof должен появиться до прямого оффера.",
            sales_function="trust_building",
            scene_ids=[f"{season_id}_scene_3"],
            hook_to_next_episode="Следующий цикл можно строить вокруг вопросов аудитории.",
        ),
    ]


def create_scene_cards(
    episodes: list[EpisodePlan],
    context: ProducerContext,
) -> list[SceneCard]:
    channel = _primary_channel(context)
    rubric = _primary_rubric(context)
    scenes: list[SceneCard] = []
    for index, episode in enumerate(episodes, start=1):
        sales_intensity = 0 if index == 1 else 1
        scenes.append(
            SceneCard(
                scene_id=episode.scene_ids[0],
                episode_id=episode.episode_id,
                channel=channel,
                format="post",
                scene_type=_scene_type_for_episode(index),
                plot_function=_plot_function_for_episode(index),
                sales_intensity=sales_intensity,
                hook=_scene_hook(episode, rubric),
                context=_scene_context(context, episode),
                conflict_or_question=episode.episode_question,
                value_point=episode.insight,
                proof_point="Use only source-backed proof after Research Agent returns evidence." if index == 3 else None,
                offer_bridge=_soft_offer_bridge(context) if index == 3 else None,
                cta=_scene_cta(index),
                next_hook=episode.hook_to_next_episode,
            )
        )
    return scenes


def create_research_directives(
    season: SeasonBible,
    scenes: list[SceneCard],
    context: ProducerContext,
    *,
    created_at: str = _DEFAULT_CREATED_AT,
) -> list[ResearchDirective]:
    rubric = _primary_rubric(context)
    content_theme = _content_theme_for_rubric(rubric)
    source_groups = _approved_source_groups_for_theme(content_theme)
    return [
        ResearchDirective(
            directive_id=f"rd_{scene.scene_id}",
            season_id=season.season_id,
            episode_id=scene.episode_id,
            scene_id=scene.scene_id,
            rubric=rubric,
            audience_segment=_primary_audience(context),
            content_theme=content_theme,
            platform_targets=_platform_targets(context),
            approved_source_groups=source_groups,
            search_goal=_research_goal(rubric, scene, content_theme),
            must_collect=list(_DIRECT_RESEARCH_FIELDS),
            must_avoid=list(_DIRECT_RESEARCH_AVOID),
            evidence_requirements=list(_EVIDENCE_REQUIREMENTS),
            priority="high" if scene.sales_intensity >= 1 else "medium",
            created_at=created_at,
        )
        for scene in scenes
    ]


def qa_producer_plan(
    *,
    brief: ProducerBrief,
    season: SeasonBible,
    episodes: list[EpisodePlan],
    scenes: list[SceneCard],
    created_at: str = _DEFAULT_CREATED_AT,
) -> ProducerQAReport:
    issues: list[str] = []
    if not brief.product_summary:
        issues.append("missing_product")
    if not brief.audience_summary:
        issues.append("missing_audience")
    if len(episodes) < 3:
        issues.append("season_needs_three_episodes")
    if any(not (scene.cta or scene.next_hook) for scene in scenes):
        issues.append("scene_missing_cta_or_next_hook")
    if calculate_direct_sales_ratio(scenes) > 0.15:
        issues.append("direct_sales_ratio_too_high")

    if issues:
        raise ValueError(f"Producer QA failed: {', '.join(issues)}")

    return ProducerQAReport(
        report_id=f"producer_qa_{season.season_id}",
        target_id=season.season_id,
        narrative_clarity=9,
        audience_relevance=9,
        sales_integration=8,
        content_variety=8,
        proof_strength=8,
        cta_clarity=8,
        operational_readiness=9,
        ethical_safety=10,
        issues=[],
        revision_notes=[],
        created_at=created_at,
    )


def create_workflow_tasks(
    *,
    research_directives: list[ResearchDirective],
    scenes: list[SceneCard],
    created_at: str = _DEFAULT_CREATED_AT,
) -> list[WorkflowTask]:
    tasks: list[WorkflowTask] = []
    for directive in research_directives:
        tasks.append(
            WorkflowTask(
                task_id=f"task_{directive.directive_id}",
                target_agent="research_agent",
                priority=directive.priority,
                payload=directive.model_dump(),
            )
        )

    for scene in scenes:
        tasks.append(
            WorkflowTask(
                task_id=f"task_brief_builder_{scene.scene_id}",
                target_agent="brief_builder",
                priority="high" if scene.sales_intensity >= 1 else "medium",
                payload={
                    "scene_id": scene.scene_id,
                    "episode_id": scene.episode_id,
                    "plot_function": scene.plot_function,
                    "sales_intensity": scene.sales_intensity,
                    "hook": scene.hook,
                },
            )
        )
    return tasks


def review_opportunities(
    opportunities: list[OpportunityCandidate],
    *,
    season_id: str,
    episode_id: str,
    scene_id: str,
    created_at: str = _DEFAULT_CREATED_AT,
) -> list[ProducerDecision]:
    return [
        review_opportunity(
            opportunity,
            season_id=season_id,
            episode_id=episode_id,
            scene_id=scene_id,
            created_at=created_at,
        )
        for opportunity in opportunities
    ]


def review_opportunity(
    opportunity: OpportunityCandidate,
    *,
    season_id: str,
    episode_id: str,
    scene_id: str,
    created_at: str = _DEFAULT_CREATED_AT,
) -> ProducerDecision:
    if _must_reject(opportunity):
        return ProducerDecision(
            decision_id=f"decision_{opportunity.opportunity_id}",
            opportunity_id=opportunity.opportunity_id,
            source_item_id=opportunity.source_item_id,
            decision="reject",
            selected_workflow=None,
            selected_platform=None,
            priority="low",
            production_intent="Reject because evidence, risk, or route does not meet Producer guardrails.",
            season_id=season_id,
            episode_id=episode_id,
            scene_id=scene_id,
            reason=_rejection_reason(opportunity),
            constraints=_producer_constraints(opportunity),
            required_evidence=list(_EVIDENCE_REQUIREMENTS),
            created_at=created_at,
        )

    if _must_hold(opportunity):
        return ProducerDecision(
            decision_id=f"decision_{opportunity.opportunity_id}",
            opportunity_id=opportunity.opportunity_id,
            source_item_id=opportunity.source_item_id,
            decision="hold",
            selected_workflow=None,
            selected_platform=None,
            priority="medium",
            production_intent="Hold until evidence is stronger or a human confirms the source boundary.",
            season_id=season_id,
            episode_id=episode_id,
            scene_id=scene_id,
            reason="Evidence exists but is not strong enough for production.",
            constraints=_producer_constraints(opportunity),
            required_evidence=list(_EVIDENCE_REQUIREMENTS),
            created_at=created_at,
        )

    workflow = _selected_workflow(opportunity)
    platform = opportunity.suggested_platform or "instagram"
    return ProducerDecision(
        decision_id=f"decision_{opportunity.opportunity_id}",
        opportunity_id=opportunity.opportunity_id,
        source_item_id=opportunity.source_item_id,
        decision="approve",
        selected_workflow=workflow,
        selected_platform=platform,
        priority=_priority_for_opportunity(opportunity),
        production_intent=_production_intent(opportunity, workflow, platform),
        season_id=season_id,
        episode_id=episode_id,
        scene_id=scene_id,
        reason="Strong enough source-backed opportunity for one selected production lane.",
        constraints=_producer_constraints(opportunity),
        required_evidence=list(_EVIDENCE_REQUIREMENTS),
        created_at=created_at,
    )


def approve_opportunity(
    opportunity: OpportunityCandidate,
    decision: ProducerDecision,
    *,
    created_at: str = _DEFAULT_CREATED_AT,
) -> ApprovedOpportunity:
    if decision.decision != "approve" or decision.selected_workflow is None or decision.selected_platform is None:
        raise ValueError("Only approved ProducerDecision can become ApprovedOpportunity")
    return ApprovedOpportunity(
        approved_id=f"approved_{opportunity.opportunity_id}",
        decision_id=decision.decision_id,
        opportunity_id=opportunity.opportunity_id,
        source_item_id=opportunity.source_item_id,
        selected_workflow=decision.selected_workflow,
        selected_platform=decision.selected_platform,
        priority=decision.priority,
        production_intent=decision.production_intent,
        core_idea=opportunity.core_idea,
        jane_adaptation_brief=opportunity.jane_adaptation_brief,
        evidence_refs=[opportunity.source_url],
        risk_flags=opportunity.risk_flags,
        season_id=decision.season_id,
        episode_id=decision.episode_id,
        scene_id=decision.scene_id,
        created_at=created_at,
    )


def calculate_direct_sales_ratio(scenes: list[SceneCard]) -> float:
    if not scenes:
        return 0.0
    direct_sales = sum(1 for scene in scenes if scene.sales_intensity == 3)
    return round(direct_sales / len(scenes), 4)


def update_from_metrics(
    *,
    season_id: str,
    metrics: MetricsSnapshot,
    created_at: str = _DEFAULT_CREATED_AT,
) -> ProducerRevision:
    actions: list[str] = []
    reasons: list[str] = []

    if metrics.story_completion_rate is not None and metrics.story_completion_rate < 0.35:
        actions.append("strengthen_hooks")
        reasons.append("low story completion suggests weak hook or missing conflict")
    if metrics.dm_count is not None and metrics.dm_count >= 20:
        actions.append("plan_episode_from_audience_questions")
        reasons.append("many DMs mean the topic is hot enough for an episode")
    if metrics.link_clicks is not None and metrics.leads is not None and metrics.link_clicks > 0 and metrics.leads == 0:
        actions.append("review_offer_bridge")
        reasons.append("clicks without leads point to offer or landing friction")
    if metrics.top_objections:
        actions.append("add_objection_handling_scene")
        reasons.append("audience objections should become explicit scenes")

    if not actions:
        actions.append("monitor_next_episode")
        reasons.append("no urgent producer correction detected")

    return ProducerRevision(
        season_id=season_id,
        target_agent="producer",
        actions=actions,
        reason="; ".join(reasons),
        created_at=created_at,
    )


def _must_reject(opportunity: OpportunityCandidate) -> bool:
    return (
        opportunity.risk_level == "high"
        or opportunity.suggested_workflow == "drop"
        or not opportunity.source_url.strip()
        or opportunity.evidence_strength_score <= 0.1
    )


def _must_hold(opportunity: OpportunityCandidate) -> bool:
    return opportunity.evidence_strength_score < 0.5 or opportunity.opportunity_score < 0.55


def _selected_workflow(opportunity: OpportunityCandidate) -> Literal["workflow_a", "workflow_b"]:
    if opportunity.suggested_workflow == "workflow_a":
        return "workflow_a"
    if opportunity.suggested_workflow == "both":
        return "workflow_a" if opportunity.source_type.startswith(("instagram_reel", "tiktok", "youtube")) else "workflow_b"
    return "workflow_b"


def _priority_for_opportunity(opportunity: OpportunityCandidate) -> Literal["low", "medium", "high", "urgent"]:
    if opportunity.opportunity_score >= 0.82:
        return "urgent"
    if opportunity.opportunity_score >= 0.68:
        return "high"
    return "medium"


def _production_intent(
    opportunity: OpportunityCandidate,
    workflow: Literal["workflow_a", "workflow_b"],
    platform: str,
) -> str:
    asset_type = "video asset" if workflow == "workflow_a" else "text asset"
    return (
        f"Create one source-backed {platform} {asset_type} for {opportunity.rubric}: "
        f"{opportunity.core_idea}"
    )


def _producer_constraints(opportunity: OpportunityCandidate) -> list[str]:
    constraints = [
        "Research Agent remains the only search/data collection layer.",
        "Do not invent facts, prices, cases, or private details.",
        "Use one selected workflow and one selected platform only.",
    ]
    if opportunity.risk_flags:
        constraints.extend(opportunity.risk_flags)
    return constraints


def _rejection_reason(opportunity: OpportunityCandidate) -> str:
    if opportunity.risk_level == "high":
        return "High-risk opportunity requires rejection or human override."
    if opportunity.suggested_workflow == "drop":
        return "Analyst route suggested drop."
    if opportunity.evidence_strength_score <= 0.1:
        return "Evidence is too weak for production."
    return "Opportunity does not meet Producer guardrails."


def _product_summary(context: ProducerContext) -> str:
    if not context.offers:
        return context.season_seed.offer_focus
    return "; ".join(
        f"{offer.name}: {offer.core_problem} -> {offer.promised_transformation}"
        for offer in context.offers
    )


def _season_title(context: ProducerContext) -> str:
    focus = context.season_seed.offer_focus.strip() or "Jane Superstar"
    return f"{focus}: блог как сериал"


def _season_thesis(brief: ProducerBrief, context: ProducerContext) -> str:
    return (
        f"Показываем, как Jane превращает {context.season_seed.offer_focus} в сериал: "
        "каждая сцена имеет инфоповод, конфликт, доказательную границу и понятный вывод."
    )


def _narrative_question(context: ProducerContext) -> str:
    if "недвижка" in " ".join(context.season_seed.rubrics_to_emphasize).lower():
        return "Можно ли видеть Bali opportunity без того, чтобы попасться на красивую поверхность?"
    return "Можно ли вести блог как живой сериал, а не как набор случайных постов?"


def _main_conflict(context: ProducerContext) -> str:
    if context.offers:
        return context.offers[0].core_problem
    return "Контент выглядит активным, но не ведёт аудиторию через понятный конфликт."


def _audience_goal(context: ProducerContext) -> str:
    if context.offers:
        return context.offers[0].promised_transformation
    return context.season_seed.season_goal


def _product_role(context: ProducerContext) -> str:
    if context.offers:
        return f"{context.offers[0].name} appears as the structured way to solve the season conflict."
    return f"{context.season_seed.offer_focus} appears as the tool, not a glued-on ad."


def _primary_channel(context: ProducerContext) -> str:
    if context.channels:
        return context.channels[0]
    if context.season_seed.channels:
        return context.season_seed.channels[0]
    return "instagram"


def _primary_rubric(context: ProducerContext) -> str:
    if context.season_seed.rubrics_to_emphasize:
        return context.season_seed.rubrics_to_emphasize[0]
    return "#заметки фаундера"


def _primary_audience(context: ProducerContext) -> str:
    if context.season_seed.audience_focus:
        return context.season_seed.audience_focus[0]
    if context.audience:
        return context.audience[0]
    return "developer_investor"


def _platform_targets(context: ProducerContext) -> list[str]:
    targets = [channel for channel in _unique([*context.channels, *context.season_seed.channels]) if channel]
    return targets or ["instagram"]


def _scene_type_for_episode(index: int) -> Literal["context", "problem_reveal", "lesson"]:
    if index == 1:
        return "context"
    if index == 2:
        return "problem_reveal"
    return "lesson"


def _plot_function_for_episode(index: int) -> Literal["introduce_context", "show_conflict", "build_trust"]:
    if index == 1:
        return "introduce_context"
    if index == 2:
        return "show_conflict"
    return "build_trust"


def _scene_hook(episode: EpisodePlan, rubric: str) -> str:
    if rubric == "#недвижка":
        return "Красивый вход в сделку редко показывает главный риск."
    if rubric == "#experience":
        return "Experience becomes strategy when it changes behavior."
    return episode.episode_question


def _scene_context(context: ProducerContext, episode: EpisodePlan) -> str:
    return f"{context.creator.name} opens the episode through the current season context: {episode.title}."


def _soft_offer_bridge(context: ProducerContext) -> str:
    if context.offers:
        return f"{context.offers[0].name} is introduced as a structured path, not a sudden pitch."
    return "The offer appears only as the logical next step after proof."


def _scene_cta(index: int) -> str:
    if index == 1:
        return "Save this if you want the next part of the series."
    if index == 2:
        return "Notice which part of this risk you have seen before."
    return "Bring this checklist to the next serious decision."


def _content_theme_for_rubric(rubric: str) -> str:
    mapping = {
        "#bali life": "bali_travel",
        "lifestyle": "founder_journey",
        "#недвижка": "land_and_legal",
        "#отношения": "founder_journey",
        "#заметки фаундера": "founder_journey",
        "#experience": "wellness_architecture",
    }
    return mapping.get(rubric, "founder_journey")


def _approved_source_groups_for_theme(content_theme: str) -> list[str]:
    if content_theme in {"land_and_legal", "market_reports", "expert_pain_bali"}:
        return ["expert_pain_bali"]
    if content_theme == "bali_travel":
        return ["bali_travel"]
    if content_theme == "wellness_architecture":
        return ["global_trends", "wellness_architecture", "boutique_hotels"]
    return ["founder_journey"]


def _research_goal(rubric: str, scene: SceneCard, content_theme: str) -> str:
    return (
        f"Find public high-performing sources for {rubric} / {content_theme} "
        f"that support scene {scene.scene_id}: {scene.conflict_or_question}"
    )


def _duration_days(date_range: str) -> int:
    normalized = date_range.lower()
    if "week" in normalized or "нед" in normalized:
        numbers = [int(token) for token in normalized.replace("-", " ").split() if token.isdigit()]
        return (numbers[0] if numbers else 2) * 7
    numbers = [int(token) for token in normalized.replace("-", " ").split() if token.isdigit()]
    return numbers[0] if numbers else 14


def _join_unique(values: list[str]) -> str:
    return ", ".join(_unique(values))


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(normalized)
    return unique_values


__all__ = [
    "ProducerRevision",
    "approve_opportunity",
    "calculate_direct_sales_ratio",
    "create_producer_brief",
    "create_research_directives",
    "create_scene_cards",
    "create_season_bible",
    "create_workflow_tasks",
    "plan_episodes",
    "qa_producer_plan",
    "review_opportunities",
    "review_opportunity",
    "run_producer_workflow",
    "update_from_metrics",
]
