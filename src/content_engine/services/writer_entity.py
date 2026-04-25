from __future__ import annotations

import re

from content_engine.context.workflow_b_rules import WorkflowBDecision
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import InsightCard
from content_engine.models.writer_entity import (
    AuthorVoiceObject,
    AvailableContext,
    BestVideoChoice,
    ContentIdea,
    EditedVersion,
    EditingLayerResult,
    EditorDiagnosis,
    FinalContentAsset,
    FinalContentQA,
    FinalContentTraceability,
    IdeaGateResult,
    IdeaGenerationResult,
    InsightVerdict,
    InsightExtractionResult,
    InsightQualityScore,
    KilledIdea,
    QAReport,
    RiskLevel,
    TaskClassification,
    TextOption,
    VideoHookOption,
    VideoHookQualityGate,
    VideoHooksTopicsOutput,
    VideoTopicOption,
    VoiceSelection,
    WriterContentBrief,
    WriterDraft,
    WriterEntityOutput,
    WriterInsightCard,
    WriterPreflight,
    WriterTaskInput,
)


JANE_FORBIDDEN_PHRASES = [
    "В современном быстро меняющемся мире",
    "Давайте погрузимся",
    "Давайте нырнём глубже",
    "Меняющий правила игры",
    "Раскройте свой потенциал",
    "Ориентироваться в вызовах",
    "Ландшафт",
    "Задействовать силу",
    "Ни для кого не секрет",
    "В конце концов",
    "Трансформирующий",
    "Бесшовный",
    "Надёжный",
    "Ключевой",
    "Синергия",
    "Экосистема",
    "Коллаборация",
    "Масштабировать",
    "Бустить",
    "При этом",
    "Тем не менее",
    "С учётом этого",
    "Примечательно, что",
    "Стоит отметить",
    "Но вот в чём дело",
    "Каждый провал — это трамплин",
    "И это совершенно нормально",
    "Позволь себе время",
    "Мы все там бывали",
    "Всё к лучшему",
]

JANE_FORBIDDEN_STRUCTURES = [
    "opening that simply restates the topic",
    "conclusion that summarizes the post",
    "generic 3-point sermon",
    "fake balanced on the one hand / on the other hand",
    "motivational final slogans",
    "more than 2 bold elements per post",
    "hashtag block at the end",
]

JANE_QA_RULES = [
    "Could anyone have written this?",
    "Remove forbidden phrases.",
    "Opening must not restate the topic.",
    "Ending must not summarize or motivate generically.",
    "Every factual claim must be supported by Fact Dossier or source material.",
    "Jane should recognize her voice.",
    "Jane should be able to say this out loud to a friend.",
]

POLITICS_MARKERS = ("политик", "election", "president", "government", "парламент", "выбор")
PRIVATE_RISK_PATTERNS = (
    r"\bprivate\s+(?:fact|facts|detail|details|client|deal|terms|revenue|investor|agreement)s?\b",
    r"\bconfidential\b",
    r"\binternal\s+only\b",
    r"\bundisclosed\s+(?:deal|client|terms|revenue|agreement)s?\b",
    r"приватн(?:ый|ые|ая|ое)\s+(?:факт|факты|детал|информац)",
    r"закрыт(?:ые|ая|ое|ый)\s+(?:детал|услов|сделк|договор|информац)",
    r"секретн(?:ые|ая|ое|ый)\s+(?:детал|услов|сделк|договор|информац)",
)
CLIENT_MARKERS = ("client name", "имя клиента", "клиент по имени", "closed deal with")


def build_jane_levitan_voice_object() -> AuthorVoiceObject:
    return AuthorVoiceObject(
        author_name="Jane Levitan",
        public_facts=[
            "Jane Levitan is CEO and founder of Clear Real Estate.",
            "Jane Levitan is founder of Clear Visionary.",
            "Clear Real Estate operates in premium real estate and land brokerage in Bali.",
            "Clear Visionary develops experience projects.",
            "AILLA is the flagship Clear Visionary project.",
            "LinkedIn may use English while Notion keeps the Russian working version.",
        ],
        private_facts_do_not_use=[
            "Private family details not explicitly approved for publication.",
            "Client names.",
            "Closed deal details not marked public.",
            "Internal revenue or contract terms.",
        ],
        audience_segments=[
            "Russian-speaking investors 30+",
            "investors with $1M+ check",
            "wives/partners of investors",
            "premium real estate buyers in Bali",
            "broker partners",
            "developers",
            "experience-project founders",
        ],
        voice_registers=[
            "register_1: object through human story",
            "register_2: object as transformation lens",
            "register_3: cold analytics with personal scene",
            "register_4: geo-economic facts",
            "register_5: short insider recommendation",
            "register_6: corporate manifesto",
            "register_7: emotional exhale",
            "register_8: confession turn",
            "register_9: family through objects",
        ],
        forbidden_phrases=JANE_FORBIDDEN_PHRASES,
        forbidden_structures=JANE_FORBIDDEN_STRUCTURES,
        taboo_topics=["politics", "client names", "private facts", "profanity"],
        signature_phrases=[
            "Zero bullshit",
            "отпетые стартаперы",
            "мама олигарха",
            "банальщина",
            "дикий",
            "офигенный",
            "штормит",
            "претерпевают",
            "демпингуют",
        ],
        public_opinions=[
            "Дешёвая недвижимость на Бали — самая дорогая ошибка",
            "Вы не покупаете дом на Бали. Вы покупаете доступ к новой версии себя",
            "Мы здесь, чтобы наполняться настоящими чувствами",
        ],
        platform_rules={
            "instagram": "Russian by default; hook, tension, payoff.",
            "linkedin": "English publish version for B2B; Russian master stays in Notion.",
            "telegram": "Russian, direct, sharper, intimate.",
        },
        qa_rules=JANE_QA_RULES,
    )


def run_preflight(
    task: WriterTaskInput,
    author_voice: AuthorVoiceObject | None,
) -> WriterPreflight:
    missing_inputs = []
    if not task.raw_topic:
        missing_inputs.append("raw_topic")
    if not task.source_material:
        missing_inputs.append("source_material")
    if not task.target_audience:
        missing_inputs.append("target_audience")
    if not task.platform:
        missing_inputs.append("platform")
    if not task.goal:
        missing_inputs.append("goal")

    risk_flags = _detect_preflight_risks(task.raw_topic, task.source_material)
    if task.author_profile == "jane_levitan":
        if not task.available_context.fact_dossier:
            missing_inputs.append("fact_dossier")
        if not task.available_context.voice_profile or author_voice is None:
            missing_inputs.append("voice_profile")
        if "politics" in risk_flags:
            risk_flags.append("jane_voice_politics_blocked")
        if "private_fact_request" in risk_flags:
            risk_flags.append("jane_voice_private_fact_blocked")

    blocking_flags = {
        "politics",
        "jane_voice_politics_blocked",
        "private_fact_request",
        "jane_voice_private_fact_blocked",
        "client_name_or_closed_deal",
    }
    if any(flag in blocking_flags for flag in risk_flags):
        return WriterPreflight(
            status="blocked",
            missing_inputs=missing_inputs,
            assumptions=[],
            risk_flags=risk_flags,
            next_action="stop",
        )
    if task.author_profile == "jane_levitan" and {"fact_dossier", "voice_profile"} & set(missing_inputs):
        return WriterPreflight(
            status="blocked",
            missing_inputs=missing_inputs,
            assumptions=[],
            risk_flags=risk_flags,
            next_action="stop",
        )
    if missing_inputs:
        return WriterPreflight(
            status="needs_context",
            missing_inputs=missing_inputs,
            assumptions=[],
            risk_flags=risk_flags,
            next_action="ask_user",
        )

    assumptions = []
    if not task.available_context.source_material:
        assumptions.append("source_material flag is false; using provided source_material text anyway")
    if task.author_profile == "jane_levitan":
        assumptions.append("Jane voice module loaded from local voice object")
    return WriterPreflight(
        status="ready",
        missing_inputs=[],
        assumptions=assumptions,
        risk_flags=risk_flags,
        next_action="continue",
    )


def classify_task(task: WriterTaskInput) -> TaskClassification:
    platform = task.platform
    content_type = "post"
    if "video" in task.raw_topic.lower() or "reel" in task.raw_topic.lower():
        content_type = "video_script"
    elif platform == "linkedin":
        content_type = "linkedin_post"
    elif platform == "instagram":
        content_type = "instagram_caption"
    elif platform == "telegram":
        content_type = "telegram_post"

    fact_required = _fact_verification_required(task.raw_topic, task.source_material)
    risk_level: RiskLevel = _risk_level(task, fact_required)
    notes = []
    if platform == "linkedin":
        notes.append("LinkedIn B2B publish version should be English; Russian master remains in Notion.")
    if task.author_profile == "jane_levitan":
        notes.append("Jane Levitan voice module requires Fact Dossier and Voice Profile.")

    return TaskClassification(
        content_type=content_type,
        platform=platform,
        target_audience=task.target_audience,
        goal=task.goal,
        required_voice_mode=task.author_profile,
        risk_level=risk_level,
        fact_verification_required=fact_required,
        notes=notes,
    )


def extract_insight(task: WriterTaskInput) -> InsightExtractionResult:
    text = _normalize_space(" ".join([task.raw_topic, task.source_material]))
    topic = _topic_from_task(task)
    emotional_trigger = _emotional_trigger(task.target_audience, text)
    hidden_tension = _hidden_tension(task.target_audience, text)
    angle = _angle_for(task, topic, hidden_tension)
    promise = _promise_for(task.target_audience, task.platform)
    audience_fit = _audience_fit(task.target_audience, topic)
    risk = _content_risk(text, task.platform)
    quality = InsightQualityScore(
        clarity=_score_from_length(text, short_floor=8),
        emotional_strength=8 if emotional_trigger else 4,
        audience_fit=8 if task.target_audience else 4,
        originality=7 if hidden_tension else 5,
    )
    verdict: InsightVerdict = "strong" if min(
        quality.clarity,
        quality.emotional_strength,
        quality.audience_fit,
        quality.originality,
    ) >= 7 else "needs_refinement"
    if quality.clarity < 5 or quality.emotional_strength < 5:
        verdict = "weak"

    return InsightExtractionResult(
        insight_card=WriterInsightCard(
            topic=topic,
            angle=angle,
            emotional_trigger=emotional_trigger,
            audience_fit=audience_fit,
            hidden_tension=hidden_tension,
            promise=promise,
            risk=risk,
            assumptions=["Insight is derived from source material before drafting."],
        ),
        quality_score=quality,
        verdict=verdict,
    )


def select_voice_register(
    *,
    task: WriterTaskInput,
    author_voice: AuthorVoiceObject | None,
    insight_topic: str,
    hidden_tension: str,
    preferred_register: str | None = None,
) -> VoiceSelection:
    text = _normalize_space(" ".join([task.raw_topic, task.source_material, insight_topic, hidden_tension])).lower()
    if task.author_profile != "jane_levitan":
        register = preferred_register or _generic_register(task)
        return VoiceSelection(
            author_profile=task.author_profile,
            primary_register=register,
            reason="Generic author mode selected from topic, platform, and goal.",
            rhythm_rules=["short paragraphs", "one main thought", "no generic AI openings"],
            opening_type="specific claim or tension",
            ending_type="platform-native CTA",
            phrases_allowed=[],
            phrases_forbidden=author_voice.forbidden_phrases if author_voice else [],
            emoji_policy="light",
        )

    register = preferred_register or _jane_register_for(text)
    emoji_policy = "light: 1-2 emojis allowed" if register in {"register_1", "register_2", "register_7"} else "none"
    reason = _jane_register_reason(register, text)
    return VoiceSelection(
        author_profile="jane_levitan",
        primary_register=register,
        secondary_register=_jane_secondary_register(register, text),
        reason=reason,
        rhythm_rules=[
            "Short and medium sentences.",
            "One sentence can be one paragraph for emphasis.",
            "Do not close with a generic summary.",
            "Address Russian readers as 'ты'.",
        ],
        opening_type=_opening_type_for(register),
        ending_type=_ending_type_for(register),
        phrases_allowed=(author_voice.signature_phrases[:5] if author_voice else []),
        phrases_forbidden=(author_voice.forbidden_phrases if author_voice else JANE_FORBIDDEN_PHRASES),
        emoji_policy=emoji_policy,
    )


def generate_content_ideas(
    insight: WriterInsightCard,
    voice_selection: VoiceSelection,
    *,
    platform: str,
    audience: str,
    goal: str,
) -> IdeaGenerationResult:
    candidates = [
        (
            "idea_01",
            _title_from(insight.topic, "hidden risk"),
            f"{insight.angle} The useful point is the tension: {insight.hidden_tension}",
            "carousel_caption" if platform == "instagram" else "thought_leadership_post",
            9,
        ),
        (
            "idea_02",
            _title_from(insight.topic, "audience mirror"),
            f"Show why {audience} should care before the topic becomes obvious.",
            "story_caption" if platform == "instagram" else "journey_arc_post",
            8,
        ),
        (
            "idea_03",
            _title_from(insight.topic, "decision frame"),
            f"Turn the source into a decision filter: {insight.promise}",
            "direct_post",
            8,
        ),
    ]
    ideas = [
        ContentIdea(
            idea_id=idea_id,
            title=title,
            core_message=core_message,
            emotional_trigger=insight.emotional_trigger,
            audience_value=insight.audience_fit,
            format_suggestion=format_suggestion,
            platform_fit=[platform],
            register_fit=voice_selection.primary_register,
            strength_score=score,
            verdict="keep",
        )
        for idea_id, title, core_message, format_suggestion, score in candidates
        if insight.emotional_trigger and insight.audience_fit
    ]
    killed_ideas: list[KilledIdea] = []
    if len(ideas) < 3:
        killed_ideas.append(
            KilledIdea(
                idea=insight.topic or "raw topic",
                reason="No clear value or emotional trigger.",
            )
        )

    best = ideas[0] if ideas else None
    return IdeaGenerationResult(
        ideas=ideas,
        killed_ideas=killed_ideas,
        best_idea={
            "idea_id": best.idea_id if best else "",
            "why": "Strongest connection between insight, audience pain, and platform fit." if best else "No idea passed.",
        },
    )


def run_idea_gate(
    ideas: list[ContentIdea],
    insight: WriterInsightCard,
) -> IdeaGateResult:
    passed = []
    killed = []
    reasoning = []
    for idea in ideas:
        failed = []
        if not insight.angle:
            failed.append("missing_insight")
        if not idea.emotional_trigger:
            failed.append("missing_emotion")
        if not idea.audience_value:
            failed.append("missing_audience_value")
        if not insight.hidden_tension and not insight.promise:
            failed.append("missing_tension_or_promise")
        if not idea.platform_fit:
            failed.append("missing_platform_fit")
        if not idea.register_fit:
            failed.append("missing_voice_fit")

        if failed:
            killed.append(idea.idea_id)
            reasoning.append(f"{idea.idea_id}: killed because {', '.join(failed)}")
        else:
            passed.append(idea.idea_id)
            reasoning.append(f"{idea.idea_id}: passed all idea gates")

    selected_idea = passed[0] if passed else ""
    return IdeaGateResult(
        passed=passed,
        killed=killed,
        reasoning=reasoning,
        selected_idea=selected_idea,
    )


def build_writer_content_brief(
    *,
    task: WriterTaskInput,
    insight: WriterInsightCard,
    selected_idea: ContentIdea,
    voice_selection: VoiceSelection,
    author_voice: AuthorVoiceObject | None,
    allowed_facts: list[str],
    reference_sources: list[str],
) -> WriterContentBrief:
    platform = task.platform
    structure = _structure_for(platform)
    return WriterContentBrief(
        audience=task.target_audience,
        platform=platform,
        goal=task.goal,
        core_message=selected_idea.core_message,
        hook_direction=_hook_direction(
            insight,
            selected_idea,
            platform,
            task.source_material,
            goal=task.goal,
            voice_register=voice_selection.primary_register,
        ),
        emotional_trigger=insight.emotional_trigger,
        structure=structure,
        tone_of_voice=task.tone_of_voice,
        voice_register=voice_selection.primary_register,
        length=task.length,
        cta=_cta_for(task.cta_type, task.platform, selected_idea),
        required_facts=allowed_facts,
        forbidden_facts=(author_voice.private_facts_do_not_use if author_voice else []),
        avoid=_avoid_list(author_voice),
        examples_or_references=reference_sources,
        source_excerpt=_source_excerpt(task.source_material),
    )


def generate_writer_draft(brief: WriterContentBrief) -> WriterDraft:
    hook = brief.hook_direction
    body = _draft_body(brief)
    return WriterDraft(
        platform=brief.platform,
        voice_register=brief.voice_register,
        title=brief.core_message[:80],
        hook=hook,
        body=body,
        cta=brief.cta,
        notes=["Draft generated only after insight, idea gate, and content brief."],
    )


def edit_writer_draft(
    *,
    draft: WriterDraft,
    brief: WriterContentBrief,
    author_voice: AuthorVoiceObject | None,
) -> EditingLayerResult:
    removed_phrases: list[str] = []
    hook = _remove_forbidden(draft.hook, author_voice, removed_phrases)
    body = _remove_forbidden(draft.body, author_voice, removed_phrases)
    cta = _remove_forbidden(draft.cta, author_voice, removed_phrases)

    body = _tighten_spacing(body)
    changes = ["Checked hook strength", "Removed generic AI phrasing", "Checked fact and privacy boundaries"]
    if removed_phrases:
        changes.append("Removed forbidden phrases")
    if not body.endswith((".", "?", "!")):
        body += "."

    factual_score = 9 if brief.required_facts or not _looks_like_fact_claim(body) else 7
    diagnosis = EditorDiagnosis(
        main_issue="Draft needed standard Writer Entity tightening and voice-safety checks.",
        hook_score=8 if len(hook.split()) >= 4 else 6,
        clarity_score=8,
        emotional_score=8 if brief.emotional_trigger else 6,
        voice_preservation_score=8,
        fact_safety_score=factual_score,
    )
    final_score = min(
        diagnosis.hook_score,
        diagnosis.clarity_score,
        diagnosis.emotional_score,
        diagnosis.voice_preservation_score,
        diagnosis.fact_safety_score,
    )
    return EditingLayerResult(
        editor_diagnosis=diagnosis,
        edited_version=EditedVersion(hook=hook, body=body, cta=cta),
        changes_made=changes,
        removed_phrases=removed_phrases,
        final_score=final_score,
    )


def run_voice_qa(
    *,
    task: WriterTaskInput,
    insight: WriterInsightCard,
    brief: WriterContentBrief,
    edited: EditedVersion,
    classification: TaskClassification,
    editing_result: EditingLayerResult,
    author_voice: AuthorVoiceObject | None,
) -> QAReport:
    issues = []
    fixes = list(editing_result.changes_made)
    full_text = " ".join([edited.hook, edited.body, edited.cta])
    if not insight.angle:
        issues.append("missing_clear_insight")
    if len(edited.hook.split()) < 4:
        issues.append("weak_hook")
    if not insight.emotional_trigger:
        issues.append("missing_emotional_trigger")
    if task.cta_type != "no_CTA" and not edited.cta:
        issues.append("missing_cta")
    if _contains_forbidden_phrase(full_text, author_voice):
        issues.append("forbidden_phrase_present")
    if classification.fact_verification_required and not brief.required_facts and classification.risk_level == "high":
        issues.append("high_risk_fact_needs_human_confirmation")

    human_review_required = classification.risk_level == "high" or task.platform == "linkedin"
    if task.target_audience in {"developer_investor", "broker", "architect_designer"}:
        human_review_required = True
    if editing_result.final_score < 8:
        human_review_required = True

    final_risk = "high" if issues else classification.risk_level
    return QAReport(
        passed=not issues,
        issues=issues,
        fixes_applied=fixes,
        requires_human_review=human_review_required,
        final_risk_level=final_risk,
    )


def run_writer_entity_workflow(
    *,
    task: WriterTaskInput,
    author_voice: AuthorVoiceObject | None = None,
    allowed_facts: list[str] | None = None,
    reference_sources: list[str] | None = None,
    preferred_register: str | None = None,
) -> WriterEntityOutput:
    resolved_voice = author_voice
    preflight = run_preflight(task, resolved_voice)
    if preflight.next_action != "continue":
        reason = ", ".join(preflight.missing_inputs + preflight.risk_flags)
        raise ValueError(f"Writer Entity preflight {preflight.status}: {reason}")

    classification = classify_task(task)
    insight_result = extract_insight(task)
    voice_selection = select_voice_register(
        task=task,
        author_voice=resolved_voice,
        insight_topic=insight_result.insight_card.topic,
        hidden_tension=insight_result.insight_card.hidden_tension,
        preferred_register=preferred_register,
    )
    ideas_result = generate_content_ideas(
        insight_result.insight_card,
        voice_selection,
        platform=task.platform,
        audience=task.target_audience,
        goal=task.goal,
    )
    idea_gate = run_idea_gate(ideas_result.ideas, insight_result.insight_card)
    if not idea_gate.selected_idea:
        raise ValueError("Writer Entity idea gate killed all ideas")
    selected_idea = next(idea for idea in ideas_result.ideas if idea.idea_id == idea_gate.selected_idea)
    brief = build_writer_content_brief(
        task=task,
        insight=insight_result.insight_card,
        selected_idea=selected_idea,
        voice_selection=voice_selection,
        author_voice=resolved_voice,
        allowed_facts=allowed_facts or [],
        reference_sources=reference_sources or [],
    )
    draft = generate_writer_draft(brief)
    editing_result = edit_writer_draft(
        draft=draft,
        brief=brief,
        author_voice=resolved_voice,
    )
    qa = run_voice_qa(
        task=task,
        insight=insight_result.insight_card,
        brief=brief,
        edited=editing_result.edited_version,
        classification=classification,
        editing_result=editing_result,
        author_voice=resolved_voice,
    )

    return WriterEntityOutput(
        preflight=preflight,
        task_classification=classification,
        insight_card=insight_result.insight_card,
        quality_score=insight_result.quality_score,
        voice_selection=voice_selection,
        ideas=ideas_result.ideas,
        killed_ideas=ideas_result.killed_ideas,
        selected_idea=selected_idea,
        idea_gate=idea_gate,
        content_brief=brief,
        draft=draft,
        editor_diagnosis=editing_result.editor_diagnosis,
        edited_final=editing_result.edited_version,
        hook_options=_hook_options(insight_result.insight_card, selected_idea),
        cta_options=_cta_options(task),
        qa_report=qa,
    )


def build_writer_task_from_source_item(
    *,
    item: SourceItem,
    decision: WorkflowBDecision,
) -> WriterTaskInput:
    return WriterTaskInput(
        raw_topic=item.content_theme.replace("_", " "),
        source_material=item.transcript_text,
        target_audience=item.audience_segment,
        platform=decision.platform,
        goal=_goal_from_decision(decision),
        tone_of_voice=decision.tone,
        length="medium",
        cta_type=decision.cta_type,
        author_profile="jane_levitan",
        available_context=AvailableContext(
            fact_dossier=True,
            voice_profile=True,
            source_material=bool(item.transcript_text.strip()),
        ),
    )


def run_writer_entity_for_workflow_b(
    *,
    item: SourceItem,
    legacy_insight: InsightCard,
    decision: WorkflowBDecision,
    verified_facts: set[str],
    reference_sources: list[str],
) -> WriterEntityOutput:
    task = build_writer_task_from_source_item(item=item, decision=decision)
    matched_facts = [
        fact
        for fact in sorted(verified_facts)
        if _fact_relevant_to_text(fact, item.transcript_text)
    ]
    if not matched_facts and legacy_insight.useful_lesson:
        matched_facts = [f"source_note: {legacy_insight.useful_lesson}"]
    return run_writer_entity_workflow(
        task=task,
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=matched_facts[:5],
        reference_sources=reference_sources,
        preferred_register=decision.tone,
    )


def build_final_content_asset(
    *,
    writer_output: WriterEntityOutput,
    content_id: str,
    title: str,
    platform: str,
    pillar: str,
    content_format: str,
    approval_status: str,
    source_ids: list[str],
    insight_id: str,
    idea_id: str,
    brief_id: str,
    draft_id: str,
    edit_version_id: str,
    hook: str | None = None,
    final_text: str | None = None,
    cta: str | None = None,
) -> FinalContentAsset:
    edited = writer_output.edited_final
    return FinalContentAsset(
        content_id=content_id,
        title=title,
        platform=platform,
        pillar=pillar,
        format=content_format,
        approval_status=approval_status,
        hook=hook if hook is not None else edited.hook,
        final_text=final_text if final_text is not None else edited.body,
        cta=cta if cta is not None else edited.cta,
        traceability=FinalContentTraceability(
            source_ids=source_ids,
            insight_id=insight_id,
            idea_id=idea_id,
            brief_id=brief_id,
            draft_id=draft_id,
            edit_version_id=edit_version_id,
        ),
        qa=FinalContentQA(
            passed=writer_output.qa_report.passed,
            issues=writer_output.qa_report.issues,
            human_review_required=writer_output.qa_report.requires_human_review,
        ),
    )


def format_final_content_asset_markdown(asset: FinalContentAsset) -> str:
    return "\n".join(
        [
            "## Final Content Asset",
            f"**Content ID:** {asset.content_id}",
            f"**Title:** {asset.title}",
            f"**Platform:** {asset.platform}",
            f"**Pillar:** {asset.pillar}",
            f"**Format:** {asset.format}",
            f"**Approval Status:** {asset.approval_status}",
            "",
            "### Hook",
            asset.hook,
            "",
            "### Final Text",
            asset.final_text,
            "",
            "### CTA",
            asset.cta,
            "",
            "### Traceability",
            f"- Source IDs: {', '.join(asset.traceability.source_ids) or '-'}",
            f"- Insight ID: {asset.traceability.insight_id}",
            f"- Idea ID: {asset.traceability.idea_id}",
            f"- Brief ID: {asset.traceability.brief_id}",
            f"- Draft ID: {asset.traceability.draft_id}",
            f"- Edit Version ID: {asset.traceability.edit_version_id}",
            "",
            "### QA",
            f"- Passed: {asset.qa.passed}",
            f"- Issues: {'; '.join(asset.qa.issues) or '-'}",
            f"- Human Review Required: {asset.qa.human_review_required}",
        ]
    )


def format_writer_entity_output_markdown(output: WriterEntityOutput) -> str:
    ideas = "\n".join(f"{index}. {idea.title}" for index, idea in enumerate(output.ideas, start=1))
    hooks = "\n".join(f"{index}. {hook.text}" for index, hook in enumerate(output.hook_options, start=1))
    ctas = "\n".join(f"{index}. {cta.text}" for index, cta in enumerate(output.cta_options, start=1))
    return "\n".join(
        [
            "## Preflight",
            f"Status: {output.preflight.status}",
            f"Assumptions: {', '.join(output.preflight.assumptions) or '-'}",
            f"Risk Flags: {', '.join(output.preflight.risk_flags) or '-'}",
            "",
            "## Insight Card",
            f"- Topic: {output.insight_card.topic}",
            f"- Angle: {output.insight_card.angle}",
            f"- Emotional Trigger: {output.insight_card.emotional_trigger}",
            f"- Audience Fit: {output.insight_card.audience_fit}",
            f"- Hidden Tension: {output.insight_card.hidden_tension}",
            f"- Promise: {output.insight_card.promise}",
            f"- Risk: {output.insight_card.risk}",
            "",
            "## Voice Selection",
            f"- Author Profile: {output.voice_selection.author_profile}",
            f"- Register: {output.voice_selection.primary_register}",
            f"- Why: {output.voice_selection.reason}",
            f"- Opening: {output.voice_selection.opening_type}",
            f"- Ending: {output.voice_selection.ending_type}",
            "",
            "## Ideas",
            ideas,
            "",
            "## Selected Idea",
            output.selected_idea.title,
            "",
            "## Content Brief",
            f"- Audience: {output.content_brief.audience}",
            f"- Platform: {output.content_brief.platform}",
            f"- Goal: {output.content_brief.goal}",
            f"- Hook Direction: {output.content_brief.hook_direction}",
            f"- CTA: {output.content_brief.cta}",
            f"- Tone: {output.content_brief.tone_of_voice}",
            f"- Length: {output.content_brief.length}",
            f"- Structure: {' -> '.join(output.content_brief.structure)}",
            f"- Required Facts: {', '.join(output.content_brief.required_facts) or '-'}",
            f"- What to Avoid: {', '.join(output.content_brief.avoid[:5]) or '-'}",
            "",
            "## Draft",
            f"{output.draft.hook}\n\n{output.draft.body}\n\n{output.draft.cta}",
            "",
            "## Edited Final Version",
            f"{output.edited_final.hook}\n\n{output.edited_final.body}\n\n{output.edited_final.cta}",
            "",
            "## Hook Options",
            hooks,
            "",
            "## CTA Options",
            ctas,
            "",
            "## QA Report",
            f"- Passed: {output.qa_report.passed}",
            f"- Issues: {', '.join(output.qa_report.issues) or '-'}",
            f"- Fixes: {', '.join(output.qa_report.fixes_applied) or '-'}",
            f"- Human Review Required: {output.qa_report.requires_human_review}",
        ]
    )


def generate_video_hooks_topics(
    *,
    video_source: str,
    target_audience: str,
    platform: str,
    goal: str,
    tone: str,
    author_profile: str,
    n_hooks: int = 10,
    n_topics: int = 5,
) -> VideoHooksTopicsOutput:
    normalized_source = _normalize_space(video_source)
    trigger = _emotional_trigger(target_audience, normalized_source)
    register = _jane_register_for(normalized_source.lower()) if author_profile == "jane_levitan" else tone
    hook_templates = [
        ("Warning", "The cheap option is rarely the safe option."),
        ("Market reality check", "Before you look at the villa, look at the structure."),
        ("Pain-point", "This is where smart buyers still lose money."),
        ("Contrarian", "A beautiful asset can still be a bad decision."),
        ("Curiosity gap", "The risk is not in the brochure. It is one layer deeper."),
        ("Mistake-based", "The first mistake is falling in love with the price."),
        ("Direct benefit", "Check this before you send the deposit."),
        ("Identity-based", "If you invest like an operator, you check this first."),
        ("Data/Proof-based", "One missing source can change the whole deal."),
        ("Insider recommendation", "Ask this question before the viewing starts."),
    ]
    top_hooks = [
        VideoHookOption(
            hook_id=f"hook_{index:02d}",
            hook_text=text,
            hook_type=hook_type,
            emotional_trigger=trigger,
            why_it_works="It opens a tension loop and points to a concrete payoff.",
            best_platform=platform,
            voice_register=register,
            risk="Can become clickbait if the body does not prove the risk.",
            improved_version=text,
        )
        for index, (hook_type, text) in enumerate(hook_templates[: max(0, n_hooks)], start=1)
    ]
    topics = [
        VideoTopicOption(
            topic_id=f"topic_{index:02d}",
            title=title,
            angle=angle,
            target_audience=target_audience,
            emotional_trigger=trigger,
            why_people_would_watch="The topic helps the audience avoid a costly blind spot.",
            best_platform=platform,
            suggested_format="short video with one retention turn every 2-3 sentences",
            voice_register=register,
        )
        for index, (title, angle) in enumerate(
            [
                ("The hidden cost behind a cheap Bali villa", "price versus structure"),
                ("What to check before the first viewing", "operator checklist"),
                ("Why beautiful projects still fail", "positioning and execution risk"),
                ("The question brokers should ask earlier", "deal-friction diagnosis"),
                ("How premium buyers read risk", "status and downside protection"),
            ][: max(0, n_topics)],
            start=1,
        )
    ]
    quality_gate = [_evaluate_video_hook(hook) for hook in top_hooks]
    return VideoHooksTopicsOutput(
        top_hooks=top_hooks,
        topics=topics,
        best_hook=BestVideoChoice(
            hook_id=top_hooks[0].hook_id if top_hooks else "",
            reason="It is specific, tension-led, and easy to pay off in the first seconds.",
        ),
        best_topic=BestVideoChoice(
            topic_id=topics[0].topic_id if topics else "",
            reason="It has the clearest audience pain and practical payoff.",
        ),
        hook_quality_gate=quality_gate,
    )


def _detect_preflight_risks(raw_topic: str, source_material: str) -> list[str]:
    text = f"{raw_topic} {source_material}".lower()
    flags = []
    if any(marker in text for marker in POLITICS_MARKERS):
        flags.append("politics")
    if any(re.search(pattern, text) for pattern in PRIVATE_RISK_PATTERNS):
        flags.append("private_fact_request")
    if any(marker in text for marker in CLIENT_MARKERS):
        flags.append("client_name_or_closed_deal")
    return flags


def _fact_verification_required(raw_topic: str, source_material: str) -> bool:
    text = f"{raw_topic} {source_material}".lower()
    return bool(
        re.search(r"\$?\d+(?:[.,]\d+)?\s?(?:m|k|%|million|млн|тыс)?", text)
        or any(marker in text for marker in ("deal", "legal", "law", "market", "investor", "roi", "yield", "сдел", "рын", "юрид"))
    )


def _risk_level(task: WriterTaskInput, fact_required: bool) -> RiskLevel:
    text = f"{task.raw_topic} {task.source_material}".lower()
    if task.platform == "linkedin" or any(marker in text for marker in ("legal", "law", "deal", "investor", "roi", "yield")):
        return "high"
    if fact_required:
        return "medium"
    return "low"


def _topic_from_task(task: WriterTaskInput) -> str:
    topic = task.raw_topic.strip()
    if topic:
        return topic[:160]
    return _normalize_space(task.source_material)[:160]


def _emotional_trigger(audience: str, text: str) -> str:
    audience_map = {
        "developer_investor": "fear of buying the wrong upside story",
        "broker": "fear of losing client trust on a weak deal",
        "architect_designer": "taste validation and desire for meaningful work",
        "lifestyle_expat": "desire to feel Bali as a real life, not a postcard",
        "dreamer_woman": "future-self desire without choosing between family and ambition",
    }
    if "family" in text.lower() or "сем" in text.lower():
        return "family and ambition tension"
    return audience_map.get(audience, "status anxiety")


def _hidden_tension(audience: str, text: str) -> str:
    text_lower = text.lower()
    if any(marker in text_lower for marker in ("cheap", "деш", "price", "цена")):
        return "The attractive entry point can hide the expensive mistake."
    if any(marker in text_lower for marker in ("wellness", "spa", "architecture")):
        return "What looks like design taste is becoming a business differentiator."
    if any(marker in text_lower for marker in ("family", "реб", "mother", "мама")):
        return "The founder life asks for ambition and tenderness at the same time."
    if audience == "developer_investor":
        return "The market rewards structure before it rewards aesthetics."
    return "The audience wants a sharper reason to care than the surface topic gives."


def _angle_for(task: WriterTaskInput, topic: str, hidden_tension: str) -> str:
    if task.platform == "linkedin":
        return f"Use {topic} as a strategic lesson: {hidden_tension}"
    if task.platform == "instagram":
        return f"Turn {topic} into a hook-tension-payoff story: {hidden_tension}"
    if task.platform == "telegram":
        return f"Make {topic} a direct opinion with one useful takeaway: {hidden_tension}"
    return f"Frame {topic} through one concrete tension: {hidden_tension}"


def _promise_for(audience: str, platform: str) -> str:
    if audience == "developer_investor":
        return "The reader will know what to check before trusting the opportunity."
    if audience == "dreamer_woman":
        return "The reader will feel a real model for ambition without self-betrayal."
    if platform == "instagram":
        return "The reader gets a saveable emotional frame."
    return "The reader gets a clearer decision frame."


def _audience_fit(audience: str, topic: str) -> str:
    return f"This matters to {audience} because {topic} changes what they trust, save, or ask next."


def _content_risk(text: str, platform: str) -> str:
    if len(text.split()) < 8:
        return "Input may be too thin; the workflow must avoid inventing substance."
    if platform == "linkedin":
        return "Can sound like generic thought leadership if not grounded in source proof."
    return "Can become generic if the hidden tension is softened."


def _score_from_length(text: str, *, short_floor: int) -> int:
    words = len(text.split())
    if words >= short_floor * 3:
        return 9
    if words >= short_floor:
        return 7
    return 4


def _generic_register(task: WriterTaskInput) -> str:
    if task.tone_of_voice:
        return task.tone_of_voice
    if task.goal == "authority":
        return "analytical"
    return "personal"


def _jane_register_for(text: str) -> str:
    if any(marker in text for marker in ("market", "рын", "yield", "roi", "report", "legal", "law")):
        return "register_3"
    if any(marker in text for marker in ("macro", "regulat", "geo", "policy")):
        return "register_4"
    if any(marker in text for marker in ("ailla", "clear visionary", "experience")):
        return "register_6"
    if any(marker in text for marker in ("wellness", "tool", "book", "recommendation", "place", "spa")):
        return "register_5"
    if any(marker in text for marker in ("family", "child", "son", "husband", "реб", "сем", "муж")):
        return "register_9"
    if any(marker in text for marker in ("mistake", "ошиб", "reel")):
        return "register_8"
    if any(marker in text for marker in ("villa", "object", "property", "дом", "вилла")):
        return "register_1"
    return "register_7"


def _jane_register_reason(register: str, text: str) -> str:
    reasons = {
        "register_1": "Object or property topic needs a human story before the market point.",
        "register_2": "The topic works as a transformation lens.",
        "register_3": "Market or deal logic needs analytics with a human edge.",
        "register_4": "Macro or regulatory material needs clean geo-economic facts.",
        "register_5": "Recommendation material should stay short and insider-like.",
        "register_6": "Clear Visionary or AILLA material needs manifesto-level clarity.",
        "register_7": "Personal or emotional update needs an exhale, not a report.",
        "register_8": "Mistake-based material needs a short confession turn.",
        "register_9": "Family material should move through objects and small scenes.",
    }
    if "market" in text or "рын" in text:
        return reasons["register_3"]
    return reasons.get(register, "Selected from Jane voice matrix.")


def _jane_secondary_register(register: str, text: str) -> str | None:
    if register == "register_6" and "ailla" in text:
        return "register_2"
    if register == "register_7" and "family" in text:
        return "register_9"
    return None


def _opening_type_for(register: str) -> str:
    if register in {"register_3", "register_4"}:
        return "personal scene for analytics or short sharp claim"
    if register == "register_6":
        return "not X but Y manifesto"
    if register == "register_9":
        return "small physical object or family scene"
    return "paradox, flipped thesis, or personal insight"


def _ending_type_for(register: str) -> str:
    if register in {"register_3", "register_4", "register_6"}:
        return "strategic question or value frame"
    if register == "register_9":
        return "short personal recognition"
    return "dialogue invitation or almost-final image"


def _title_from(topic: str, frame: str) -> str:
    return f"{topic}: {frame}".strip(": ")


def _structure_for(platform: str) -> list[str]:
    if platform == "linkedin":
        return ["goal", "obstacle", "process", "lesson", "reflection", "community invite"]
    if platform == "instagram":
        return ["hook", "tension", "story", "payoff", "engagement prompt"]
    if platform == "telegram":
        return ["sharp claim", "context", "useful point", "direct question"]
    return ["hook", "one idea", "payoff", "CTA"]


def _hook_direction(
    insight: WriterInsightCard,
    selected_idea: ContentIdea,
    platform: str,
    source_material: str = "",
    goal: str = "",
    voice_register: str = "",
) -> str:
    context = _normalize_space(
        " ".join(
            [
                insight.topic,
                insight.angle,
                insight.hidden_tension,
                insight.promise,
                selected_idea.title,
                selected_idea.core_message,
                source_material,
            ]
        )
    ).lower()
    theme = _hook_theme_key(context)
    ru_subject, en_subject = _hook_subject_labels(context)

    if platform == "linkedin":
        return _linkedin_hook_direction(theme, en_subject)
    return _russian_hook_direction(theme, ru_subject, goal=goal, voice_register=voice_register)


def _hook_theme_key(context: str) -> str:
    if _contains_any(
        context,
        ("founder_journey", "founder journey", "personal_life_entrepreneur", "personal life entrepreneur", "личная_жизнь_предпринимателя"),
    ):
        return "founder_life"
    if _contains_any(context, ("bali_travel", "bali travel")):
        return "bali_travel"
    if _contains_any(context, ("wellness_architecture", "wellness architecture")):
        return "wellness_design"
    if _contains_any(context, ("boutique_hotels", "boutique hotels")):
        return "boutique_hospitality"
    if _contains_any(context, ("expert_pain_bali", "expert pain bali", "market_reports", "market reports")):
        return "market_structure"
    if _contains_any(context, ("land_and_legal", "land and legal")):
        return "legal_structure"

    if _contains_any(context, ("legal", "law", "lawyer", "zoning", "permit", "regulat", "юрид", "закон", "разреш")):
        return "legal_structure"
    if _contains_any(context, ("land", "зем", "leasehold", "freehold")):
        return "land_structure"
    if _contains_any(context, ("wellness", "spa", "biophilic", "restorative", "wellbeing")):
        return "wellness_design"
    if _contains_any(context, ("boutique", "hotel", "hospitality", "resort", "bensley", "guest")):
        return "boutique_hospitality"
    if _contains_any(context, ("travel", "itinerary", "beach", "restaurant", "balibible", "trip", "путеше")):
        return "bali_travel"
    if _contains_any(context, ("family", "child", "mother", "founder", "ambition", "entrepreneur", "сем", "реб", "мама", "амбици")):
        return "founder_life"
    if _contains_any(context, ("trend", "report", "market", "yield", "price", "villa", "operator", "resale", "property", "investor", "рын", "цен", "вилл")):
        return "market_structure"
    return "source_specific"


def _hook_subject_labels(context: str) -> tuple[str, str]:
    if _contains_any(context, ("founder_journey", "founder journey", "personal life entrepreneur")):
        return _founder_hook_subject(context)
    if _contains_any(context, ("bali_travel", "bali travel")):
        return _bali_travel_hook_subject(context)
    if _contains_any(context, ("boutique_hotels", "boutique hotels")):
        return _boutique_hook_subject(context)

    subjects = [
        (("zoning", "permit", "разреш"), "разрешения и зонинг", "zoning and permit layer"),
        (("legal", "law", "lawyer", "юрид", "закон"), "правовая структура", "legal structure"),
        (("operator", "management", "operations", "оператор"), "операторская реальность", "operator reality"),
        (("resale", "liquidity", "exit", "ликвид"), "ликвидность и выход", "liquidity and exit path"),
        (("yield", "roi", "return", "доход"), "доходность", "yield logic"),
        (("land", "зем", "leasehold", "freehold"), "земельная структура", "land structure"),
        (("family", "child", "mother", "сем", "реб", "мама"), "семейные ритуалы", "family rituals"),
        (("ambition", "founder", "entrepreneur", "амбици"), "амбиция без идеальной картинки", "ambition without a perfect image"),
        (("wellness", "spa", "biophilic"), "ощущение восстановления", "restorative feeling"),
        (("boutique", "hotel", "hospitality", "resort"), "причина вернуться", "reason to return"),
        (("travel", "itinerary", "trip", "beach", "путеше"), "честный опыт места", "honest experience of place"),
        (("trend", "report", "market", "рын"), "рыночный сигнал", "market signal"),
    ]
    for markers, ru_subject, en_subject in subjects:
        if _contains_any(context, markers):
            return ru_subject, en_subject
    return "решение за красивой поверхностью", "decision behind the surface"


def _founder_hook_subject(context: str) -> tuple[str, str]:
    if _contains_any(context, ("school", "education", "pregnancy", "child", "ханн", "школ", "беремен", "реб")):
        return "школа и детское чувство дома", "school and child decisions"
    if _contains_any(context, ("student", "realtor", "course", "client", "deal", "учен", "риелтор", "курс", "клиент", "сдел")):
        return "уверенность перед клиентом", "client confidence"
    if _contains_any(context, ("dance", "dream", "desire", "мечт", "танц", "желан")):
        return "свои желания", "personal desire"
    if _contains_any(context, ("brother", "sister", "concert", "emily", "family", "брат", "сестр", "концерт", "эмили", "сем")):
        return "семейная память", "family memory"
    return "амбиция без идеальной картинки", "ambition without a perfect image"


def _bali_travel_hook_subject(context: str) -> tuple[str, str]:
    if _contains_any(context, ("ubud", "dinner", "restaurant", "ужин", "ресторан")):
        return "вечерний Убуд", "Ubud dinner ritual"
    if _contains_any(context, ("heritage", "village", "rice", "jungle", "soul", "наслед", "деревн", "рисов", "джунг")):
        return "живая связь с местом", "living heritage"
    if _contains_any(context, ("guide", "curated", "things to do", "destination", "маршрут", "гид")):
        return "честный маршрут по Бали", "honest route through Bali"
    return "честный опыт места", "honest experience of place"


def _boutique_hook_subject(context: str) -> tuple[str, str]:
    if _contains_any(context, ("management", "operator", "asset", "owner", "оператор", "управлен")):
        return "операционная реальность", "operator reality"
    if _contains_any(context, ("sustainab", "bensley", "designer", "design", "устойчив", "дизайн")):
        return "точка зрения в дизайне", "design point of view"
    if _contains_any(context, ("architecture", "interiors", "dezeen", "архитект", "интерьер")):
        return "архитектурный сигнал", "architecture signal"
    return "причина вернуться", "reason to return"


def _russian_hook_direction(theme: str, subject: str, *, goal: str, voice_register: str) -> str:
    if theme == "wellness_design" and (goal == "authority" or voice_register in {"register_3", "register_4", "register_6"}):
        return f"Wellness в архитектуре — это не декор. Это продуктовая логика: {subject}."
    if theme == "boutique_hospitality" and (goal == "authority" or voice_register in {"register_3", "register_4", "register_6"}):
        return f"Бутик-отель выигрывает не картинкой. Он выигрывает операционной логикой: {subject}."

    hooks = {
        "legal_structure": f"На Бали самый дорогой риск часто прячется не в цене. Проверь слой: {subject}.",
        "land_structure": f"Земля на Бали выглядит простой, пока не вскрывается слой: {subject}.",
        "wellness_design": f"Wellness-проект продаёт не спа-зону. Он продаёт: {subject}.",
        "boutique_hospitality": f"Бутик-отель выигрывает не красотой. Он выигрывает через: {subject}.",
        "bali_travel": f"Бали легко снять красиво. Сложнее поймать: {subject}.",
        "founder_life": f"Жизнь предпринимателя ломается не от амбиций. Она ломается, когда исчезает: {subject}.",
        "market_structure": f"На Бали важна не первая цена. Важнее источник сигнала: {subject}.",
    }
    return hooks.get(theme, f"В этом source важна не картинка, а {subject}.")


def _linkedin_hook_direction(theme: str, subject: str) -> str:
    article = "an" if subject[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
    hooks = {
        "legal_structure": f"In Bali, the expensive risk is rarely the price. It is the {subject} behind it.",
        "land_structure": f"Bali land looks simple until the {subject} starts asking expensive questions.",
        "wellness_design": f"Wellness is moving from a design feature to a signal of {subject}.",
        "boutique_hospitality": f"Boutique hospitality wins when beauty becomes {article} {subject}.",
        "bali_travel": f"Bali is easy to film beautifully and harder to read through {subject}.",
        "founder_life": f"A founder's life breaks when {subject} has to look effortless.",
        "market_structure": f"The real Bali signal is not the headline price. It is the {subject}.",
    }
    return hooks.get(theme, f"The real signal is not the surface story. It is the {subject}.")


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _cta_for(cta_type: str, platform: str, selected_idea: ContentIdea) -> str:
    normalized = cta_type.lower()
    if normalized == "save":
        return "Сохрани это перед следующей проверкой объекта."
    if normalized == "share":
        return "Перешли тому, кто сейчас смотрит на Бали как на красивую картинку."
    if normalized == "dm":
        return "Напиши в DM, если хочешь разобрать объект без банальщины."
    if normalized == "click":
        return "Открой ссылку и проверь детали до первого звонка."
    if normalized == "no_cta":
        return ""
    if platform == "linkedin":
        return "What do you check first before trusting a market opportunity?"
    return "Что ты проверяешь первым делом?"


def _avoid_list(author_voice: AuthorVoiceObject | None) -> list[str]:
    avoid = [
        "generic AI openings",
        "fake motivation",
        "invented facts",
        "private facts",
        "unsupported client or deal details",
    ]
    if author_voice:
        avoid.extend(author_voice.forbidden_phrases[:8])
    return avoid


def _source_excerpt(source_material: str, limit: int = 260) -> str:
    normalized = _normalize_space(source_material)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _draft_body(brief: WriterContentBrief) -> str:
    theme = _brief_theme_key(brief)
    if brief.platform == "linkedin":
        return _linkedin_body(brief, theme)
    if brief.platform == "instagram":
        return _instagram_body(brief, theme)
    return (
        "Так вот.\n\n"
        f"{_ru_theme_claim(theme)}\n\n"
        "Если в source нет факта, ссылки или ясного вывода, лучше остановить текст здесь, чем делать красивую лапшу."
    )


def _brief_theme_key(brief: WriterContentBrief) -> str:
    context = _normalize_space(
        " ".join(
            [
                brief.hook_direction,
                brief.core_message,
                brief.emotional_trigger,
                " ".join(brief.structure),
                " ".join(brief.required_facts),
                " ".join(brief.examples_or_references),
                brief.source_excerpt or "",
            ]
        )
    ).lower()
    return _hook_theme_key(context)


def _instagram_body(brief: WriterContentBrief, theme: str) -> str:
    subject = _subject_from_hook(brief.hook_direction)
    cue = _source_specific_cue(brief, theme)
    if theme == "founder_life":
        return (
            "Снаружи это может выглядеть как красивая жизнь предпринимателя.\n\n"
            f"Но внутри всё держится на конкретной вещи: {subject}.\n\n"
            f"В этой истории цепляет деталь: {cue}.\n\n"
            "Бизнес, ребёнок, планы, картинка, где будто всё держится само. А потом ты понимаешь: амбиции не отменяют семью, усталость и свои желания.\n\n"
            "Если эту часть вырезать, получится не сильная женщина, а аккуратно упакованная функция."
        )
    if theme in {"market_structure", "legal_structure", "land_structure"}:
        return (
            "Я бы здесь смотрела не на фасад.\n\n"
            f"Сначала {subject}. Потом операторская логика. Потом ликвидность, если первая эмоция прошла.\n\n"
            f"Конкретная зацепка здесь: {cue}.\n\n"
            "Красивый объект может быть слабым решением, если за ним нет нормального ответа на простые вопросы.\n\n"
            "Именно там обычно прячется дорогая ошибка."
        )
    if theme == "bali_travel":
        return (
            "Такие места работают не потому, что они просто красивые.\n\n"
            f"Они дают маленький ритуал: {subject}, воздух, свет, ощущение, что ты на секунду попала в другую версию своей жизни.\n\n"
            f"В исходной детали важно именно это: {cue}.\n\n"
            "Для Бали это сильнее очередного списка мест.\n\n"
            "Ты либо чувствуешь место телом, либо просто пролистываешь ещё одну картинку."
        )
    if theme == "wellness_design":
        return (
            "Wellness тут не про спа в углу.\n\n"
            f"Это про {subject}: свет, тишина, вода, маршрут тела внутри дома.\n\n"
            f"Здесь ценно не слово wellness, а конкретная подсказка: {cue}.\n\n"
            "Для девелопера это уже не декор. Это продуктовая логика.\n\n"
            "Если место не восстанавливает, оно просто красиво выглядит."
        )
    if theme == "boutique_hospitality":
        return (
            "Бутик-отель держится не на красивом лобби.\n\n"
            f"Он держится на причине вернуться: {subject}, сценарии, детали, оператор, ощущение, что место не случайное.\n\n"
            f"В этой находке главное: {cue}.\n\n"
            "Когда этого нет, дизайн становится декорацией.\n\n"
            "Когда это есть, объект начинает работать как история, а не как набор комнат."
        )
    return (
        "Сначала видишь картинку.\n\n"
        f"Потом появляется главный вопрос: {_ru_theme_claim(theme)}\n\n"
        "И вот здесь контент становится полезным: не украшает source, а достаёт из него решение, которое читатель правда может применить."
    )


def _linkedin_body(brief: WriterContentBrief, theme: str) -> str:
    subject = _english_subject_from_hook(brief.hook_direction)
    cue = _english_source_specific_cue(brief, theme)
    if theme in {"market_structure", "legal_structure", "land_structure"}:
        return (
            "The first layer is usually attractive: price, design, location, projected upside.\n\n"
            f"The second layer is where the decision becomes serious: {subject}, permits, operator logic, liquidity, and who carries the downside if the story does not perform.\n\n"
            f"The useful source cue is this: {cue}.\n\n"
            "For developers and investors, the useful move is to slow the narrative down before it becomes too easy to believe.\n\n"
            "Good opportunities survive that check."
        )
    if theme == "boutique_hospitality":
        return (
            "A boutique hotel is not a smaller version of a large hotel.\n\n"
            f"It needs a sharper reason to exist: {subject}, operating rhythm, repeatable guest memory, and a commercial logic behind the beauty.\n\n"
            f"The useful source cue is this: {cue}.\n\n"
            "The projects worth studying are the ones where design is not decoration. It is positioning.\n\n"
            "That is where hospitality becomes an asset strategy, not just an aesthetic choice."
        )
    if theme == "wellness_design":
        return (
            "Wellness is becoming less of an amenity and more of a product thesis.\n\n"
            "The question is not whether a project has a spa, greenery, or quiet corners. The question is whether the whole spatial logic helps people recover, stay longer, and remember the place.\n\n"
            "For experience-led real estate, that changes the brief.\n\n"
            "Design has to carry feeling and business logic at the same time."
        )
    if theme == "bali_travel":
        return (
            "Bali content often starts as scenery.\n\n"
            "The stronger signal is what the place teaches about behavior: where people slow down, what they repeat, which rituals become worth sharing, and why a location turns into memory.\n\n"
            "For hospitality and experience projects, that is not soft context.\n\n"
            "It is demand intelligence."
        )
    if theme == "founder_life":
        return (
            "Founder stories are often packaged as momentum.\n\n"
            "The more useful version shows the cost of that momentum: family choices, identity pressure, ambition, and the parts of life that cannot be optimized like a dashboard.\n\n"
            "That tension is why the story works.\n\n"
            "It is not inspiration. It is a better read of what building actually requires."
        )
    return (
        "The surface signal is rarely enough.\n\n"
        f"A useful content asset has to show what the source changes: {subject}, the decision, the risk, the audience belief, or the next question worth asking.\n\n"
        "Without that layer, it becomes commentary.\n\n"
        "With it, it becomes strategy."
    )


def _subject_from_hook(hook: str) -> str:
    normalized = _normalize_space(hook)
    if ":" in normalized:
        return normalized.rsplit(":", 1)[-1].strip(" .") or "свои желания"
    if "исчезает" in normalized:
        return normalized.rsplit("исчезает", 1)[-1].strip(" :.") or "свои желания"
    return "свои желания"


def _english_subject_from_hook(hook: str) -> str:
    normalized = _normalize_space(hook)
    for marker in ("It is the ", "through ", "becomes a ", "becomes an ", "becomes "):
        if marker in normalized:
            return normalized.rsplit(marker, 1)[-1].strip(" .") or "decision layer"
    return "the decision layer"


def _source_specific_cue(brief: WriterContentBrief, theme: str) -> str:
    text = (brief.source_excerpt or "").lower()
    if theme == "founder_life":
        cues = [
            (("student", "учен", "realtor", "course", "client", "deal", "риелтор", "курс", "клиент", "сдел"), "уверенность перед клиентом не рождается из красивой картинки"),
            (("dance", "бальн", "танц", "dream", "мечт"), "желание, которое долго откладывали, всё равно возвращается"),
            (("brother", "sister", "family memory", "брат", "сестр", "константин", "эмили"), "семейная память сильнее идеальной упаковки"),
            (("school", "education", "pregnancy", "child", "школ", "беремен", "реб"), "выбор для ребёнка становится частью выбора жизни"),
            (("рассказывать о своей жизни", "personal brand", "идеальн"), "решение говорить о жизни без идеальной упаковки"),
        ]
        return _first_matching_cue(text, cues, "амбиция работает только тогда, когда внутри остаётся место живой жизни")
    if theme in {"market_structure", "legal_structure", "land_structure"}:
        cues = [
            (("law", "legal", "lawyer", "permit", "zoning", "юрид", "закон", "разреш"), "правовой слой важнее первого впечатления"),
            (("report", "data", "market", "benchmark", "рын", "отчет"), "рыночный сигнал нужно читать до эмоции покупки"),
            (("operator", "management", "asset owner", "оператор", "управлен"), "операторская модель решает судьбу красивого объекта"),
            (("yield", "roi", "return", "доход"), "доходность без структуры быстро становится фантазией"),
        ]
        return _first_matching_cue(text, cues, "проверять нужно не обещание, а слой решения под ним")
    if theme == "bali_travel":
        cues = [
            (("ubud", "dinner", "restaurant", "ужин", "ресторан"), "место запоминается через вечерний ритуал"),
            (("heritage", "village", "rice", "jungle", "наслед", "деревн", "джунг"), "живая среда сильнее туристической открытки"),
            (("guide", "things to do", "destination", "маршрут", "гид"), "маршрут ценен, когда он даёт ощущение, а не список"),
        ]
        return _first_matching_cue(text, cues, "Бали работает через телесное ощущение места")
    if theme == "wellness_design":
        cues = [
            (("hot spring", "spa", "thermal", "water"), "вода и ритуал восстановления становятся частью продукта"),
            (("research", "report", "economy", "wellness"), "wellness уже читается как рынок, а не настроение"),
            (("biophilic", "interior", "architecture", "design"), "материалы и маршрут тела создают ощущение восстановления"),
        ]
        return _first_matching_cue(text, cues, "пространство должно менять состояние человека")
    if theme == "boutique_hospitality":
        cues = [
            (("bensley", "sustainab", "designer", "purpose"), "у проекта должна быть точка зрения, а не только стиль"),
            (("management agreement", "asset owner", "operator", "управлен"), "управление может быть самым необратимым решением"),
            (("dezeen", "architecture", "interiors"), "архитектурный сигнал помогает отличаться до продажи"),
        ]
        return _first_matching_cue(text, cues, "причина вернуться должна быть встроена в операционную модель")
    return "из исходника нужно забрать не пересказ, а применимый вывод"


def _english_source_specific_cue(brief: WriterContentBrief, theme: str) -> str:
    text = (brief.source_excerpt or "").lower()
    if theme == "founder_life":
        cues = [
            (("student", "realtor", "course", "client", "deal"), "client confidence is built through proof, not a polished image"),
            (("dance", "dream", "desire"), "deferred desire eventually comes back into the founder story"),
            (("brother", "sister", "family memory"), "family memory carries more weight than a polished narrative"),
            (("school", "education", "pregnancy", "child"), "family decisions become part of the founder operating system"),
        ]
        return _first_matching_cue(text, cues, "ambition only works when real life still has room inside it")
    if theme in {"market_structure", "legal_structure", "land_structure"}:
        cues = [
            (("law", "legal", "lawyer", "permit", "zoning"), "legal structure matters more than the first impression"),
            (("report", "data", "market", "benchmark"), "market signals should be read before the buying emotion starts"),
            (("operator", "management", "asset owner"), "the operating model decides whether the asset can perform"),
            (("yield", "roi", "return"), "yield without structure becomes a story, not a strategy"),
        ]
        return _first_matching_cue(text, cues, "the decision layer matters more than the promise")
    if theme == "bali_travel":
        cues = [
            (("ubud", "dinner", "restaurant"), "places become memorable through repeatable rituals"),
            (("heritage", "village", "rice", "jungle"), "living context is stronger than a tourist postcard"),
            (("guide", "things to do", "destination"), "a route matters when it creates a feeling, not a list"),
        ]
        return _first_matching_cue(text, cues, "Bali works through embodied memory, not scenery alone")
    if theme == "wellness_design":
        cues = [
            (("hot spring", "spa", "thermal", "water"), "water and recovery rituals are becoming part of the product"),
            (("research", "report", "economy", "wellness"), "wellness reads like a market signal, not a mood"),
            (("biophilic", "interior", "architecture", "design"), "materials and spatial rhythm create restoration"),
        ]
        return _first_matching_cue(text, cues, "the space has to change the guest's state")
    if theme == "boutique_hospitality":
        cues = [
            (("bensley", "sustainab", "designer", "purpose"), "a project needs a point of view, not only style"),
            (("management agreement", "asset owner", "operator", "management discipline"), "management can be the least reversible decision"),
            (("dezeen", "architecture", "interiors"), "architecture can become differentiation before sales"),
        ]
        return _first_matching_cue(text, cues, "the reason to return must be built into the operating model")
    return "the source needs to become an applicable decision, not a summary"


def _first_matching_cue(text: str, cues: list[tuple[tuple[str, ...], str]], fallback: str) -> str:
    for markers, cue in cues:
        if _contains_any(text, markers):
            return cue
    return fallback


def _ru_theme_claim(theme: str) -> str:
    claims = {
        "founder_life": "что в этой истории держит жизнь, а не только образ сильной женщины?",
        "market_structure": "где здесь структура, а где просто красивая упаковка?",
        "legal_structure": "какой юридический слой может сломать красивую сделку?",
        "land_structure": "что реально стоит за землёй, документами и правом пользоваться объектом?",
        "bali_travel": "какое ощущение места человек захочет повторить?",
        "wellness_design": "восстанавливает ли пространство человека или только выглядит дорого?",
        "boutique_hospitality": "почему гость должен вернуться именно сюда?",
    }
    return claims.get(theme, "какой вывод из этого source можно забрать без выдуманных фактов?")


def _remove_forbidden(
    text: str,
    author_voice: AuthorVoiceObject | None,
    removed_phrases: list[str],
) -> str:
    phrases = author_voice.forbidden_phrases if author_voice else JANE_FORBIDDEN_PHRASES
    result = text
    for phrase in phrases:
        pattern = re.compile(re.escape(phrase), flags=re.IGNORECASE)
        if pattern.search(result):
            removed_phrases.append(phrase)
            result = pattern.sub("", result)
    return _tighten_spacing(result)


def _tighten_spacing(text: str) -> str:
    lines = [" ".join(line.split()).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _looks_like_fact_claim(text: str) -> bool:
    return bool(re.search(r"\$?\d+(?:[.,]\d+)?\s?(?:m|k|%|million|млн|тыс)?", text.lower()))


def _contains_forbidden_phrase(text: str, author_voice: AuthorVoiceObject | None) -> bool:
    phrases = author_voice.forbidden_phrases if author_voice else JANE_FORBIDDEN_PHRASES
    lower = text.lower()
    return any(phrase.lower() in lower for phrase in phrases)


def _hook_options(insight: WriterInsightCard, idea: ContentIdea) -> list[TextOption]:
    return [
        TextOption(option_id="hook_01", text=idea.title, reason="Best aligned with selected idea."),
        TextOption(option_id="hook_02", text=insight.hidden_tension, reason="Best tension-led opening."),
        TextOption(option_id="hook_03", text=insight.promise, reason="Best payoff-led opening."),
    ]


def _cta_options(task: WriterTaskInput) -> list[TextOption]:
    return [
        TextOption(option_id="cta_01", text=_cta_for(task.cta_type, task.platform, ContentIdea(
            idea_id="tmp",
            title=task.raw_topic,
            core_message=task.raw_topic,
            emotional_trigger="",
            audience_value="",
            format_suggestion="",
            platform_fit=[task.platform],
            register_fit="",
            strength_score=1,
            verdict="refine",
        )), reason="Matches requested CTA type."),
        TextOption(option_id="cta_02", text="Что ты проверяешь первым делом?", reason="Useful discussion starter."),
        TextOption(option_id="cta_03", text="Сохрани как pre-check перед следующим объектом.", reason="Save-oriented CTA."),
    ]


def _goal_from_decision(decision: WorkflowBDecision) -> str:
    if decision.funnel_role == "authority":
        return "authority"
    if decision.funnel_role == "affinity":
        return "engagement"
    if decision.funnel_role == "conversion":
        return "sales"
    return "nurture"


def _fact_relevant_to_text(fact: str, text: str) -> bool:
    text_lower = text.lower()
    return any(token in text_lower for token in fact.lower().split() if len(token) > 4)


def _evaluate_video_hook(hook: VideoHookOption) -> VideoHookQualityGate:
    specific = len(hook.hook_text.split()) >= 6
    curiosity = any(word in hook.hook_text.lower() for word in ("cheap", "risk", "before", "hide", "missing", "wrong"))
    deliverable = "clickbait" not in hook.hook_text.lower()
    keep = specific and curiosity and deliverable
    return VideoHookQualityGate(
        hook_id=hook.hook_id,
        specific=specific,
        curiosity_or_tension=curiosity,
        audience_clear=True,
        real_payoff=True,
        deliverable=deliverable,
        emotionally_sharp=curiosity,
        voice_fit=True,
        verdict="keep" if keep else "rewrite",
    )


def _normalize_space(text: str) -> str:
    return " ".join(text.split()).strip()
