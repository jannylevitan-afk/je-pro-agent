from content_engine.models.writer_entity import AvailableContext, WriterTaskInput
from content_engine.services.writer_entity import (
    MAX_JANE_ANALYST_REVIEW_PASSES,
    build_final_content_asset,
    build_jane_levitan_voice_object,
    format_final_content_asset_markdown,
    generate_video_hooks_topics,
    run_preflight,
    run_writer_entity_workflow,
    select_voice_register,
)


def make_task(**overrides: object) -> WriterTaskInput:
    data = {
        "raw_topic": "Bali villa market risk",
        "source_material": (
            "A source note says cheap Bali villas often hide deal-structure risk, "
            "operator weakness, and positioning mistakes."
        ),
        "target_audience": "developer_investor",
        "platform": "linkedin",
        "goal": "authority",
        "tone_of_voice": "analytical",
        "length": "medium",
        "cta_type": "comment",
        "author_profile": "jane_levitan",
        "available_context": AvailableContext(
            fact_dossier=True,
            voice_profile=True,
            source_material=True,
        ),
    }
    data.update(overrides)
    return WriterTaskInput(**data)


def test_preflight_blocks_jane_without_fact_and_voice_context() -> None:
    task = make_task(
        available_context=AvailableContext(
            fact_dossier=False,
            voice_profile=False,
            source_material=True,
        )
    )

    preflight = run_preflight(task, author_voice=None)

    assert preflight.status == "blocked"
    assert "fact_dossier" in preflight.missing_inputs
    assert "voice_profile" in preflight.missing_inputs
    assert preflight.next_action == "stop"


def test_preflight_does_not_block_public_word_private_or_closed_in_normal_context() -> None:
    task = make_task(
        raw_topic="Broker education and Bali honeymoon villas",
        source_material=(
            "Риелтор закрыл первую сделку. "
            "The travel source mentions a private villa and honeymoon itinerary."
        ),
    )

    preflight = run_preflight(task, author_voice=build_jane_levitan_voice_object())

    assert preflight.status == "ready"
    assert "private_fact_request" not in preflight.risk_flags


def test_preflight_blocks_actual_private_deal_details() -> None:
    task = make_task(
        raw_topic="Use private client details",
        source_material="Use confidential internal only deal terms from a private client.",
    )

    preflight = run_preflight(task, author_voice=build_jane_levitan_voice_object())

    assert preflight.status == "blocked"
    assert "private_fact_request" in preflight.risk_flags


def test_jane_register_selector_uses_market_analytics_register() -> None:
    task = make_task(raw_topic="Bali market report and rental yield risk")
    voice = build_jane_levitan_voice_object()

    selection = select_voice_register(
        task=task,
        author_voice=voice,
        insight_topic="Bali market report",
        hidden_tension="Cheap price can hide structural downside.",
    )

    assert selection.primary_register == "register_3"
    assert "market" in selection.reason.lower()
    assert selection.emoji_policy == "none"


def test_writer_entity_workflow_returns_full_step_by_step_contract() -> None:
    result = run_writer_entity_workflow(
        task=make_task(),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Clear Real Estate operates under the Zero bullshit positioning."],
        reference_sources=["https://example.com/source"],
    )

    assert result.preflight.status == "ready"
    assert result.task_classification.content_type == "linkedin_post"
    assert result.insight_card.topic
    assert 3 <= len(result.ideas) <= 5
    assert result.idea_gate.selected_idea == result.selected_idea.idea_id
    assert result.content_brief.hook_direction == result.draft.hook
    assert result.edited_final.body
    assert result.hook_options
    assert result.cta_options
    assert result.qa_report.requires_human_review is True


def test_writer_entity_uses_source_specific_hook_direction_per_source() -> None:
    family_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="Личная жизнь предпринимателя",
            source_material=(
                "Founder story about keeping ambition alive while raising a child, "
                "protecting family rituals, and refusing to turn life into a perfect Instagram postcard."
            ),
            target_audience="dreamer_woman",
            platform="instagram",
            goal="affinity",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers founder family life and ambition tension."],
        reference_sources=["https://example.com/founder-life"],
    )
    market_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="Bali villa market risk",
            source_material=(
                "Market source says underpriced Bali villas can hide zoning, legal structure, "
                "permit, operator, and resale risk."
            ),
            target_audience="developer_investor",
            platform="instagram",
            goal="authority",
            tone_of_voice="analytical",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers Bali villa legal structure and operator risk."],
        reference_sources=["https://example.com/bali-market"],
    )

    family_hook = family_result.content_brief.hook_direction
    market_hook = market_result.content_brief.hook_direction

    assert family_hook != market_hook
    assert family_hook != "Дешёвая картинка часто оказывается самой дорогой ошибкой."
    assert market_hook != "Дешёвая картинка часто оказывается самой дорогой ошибкой."
    assert any(marker in family_hook.lower() for marker in ("сем", "жизн", "амбици"))
    assert any(marker in market_hook.lower() for marker in ("бали", "структур", "риск", "цен"))


def test_writer_entity_uses_lane_specific_hook_direction_for_same_source() -> None:
    source_material = (
        "A wellness architecture source explains spa flow, biophilic design, and restorative feeling "
        "inside premium hospitality."
    )
    lifestyle_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="wellness architecture",
            source_material=source_material,
            target_audience="architect_designer",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers wellness architecture and restorative feeling."],
        reference_sources=["https://example.com/wellness"],
        preferred_register="register_2",
    )
    professional_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="wellness architecture",
            source_material=source_material,
            target_audience="architect_designer",
            platform="instagram",
            goal="authority",
            tone_of_voice="analytical",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers wellness architecture and restorative feeling."],
        reference_sources=["https://example.com/wellness"],
        preferred_register="register_6",
    )

    assert lifestyle_result.content_brief.hook_direction != professional_result.content_brief.hook_direction
    assert "ощущ" in lifestyle_result.content_brief.hook_direction.lower()
    assert any(marker in professional_result.content_brief.hook_direction.lower() for marker in ("логик", "архитект", "продукт"))


def test_writer_entity_prioritizes_declared_topic_over_incidental_keywords() -> None:
    founder_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material=(
                "Architect founder in Bali designs spaces you can touch, but this source is about family rituals, "
                "a child, ambition, and the cost of performing a perfect life."
            ),
            target_audience="dreamer_woman",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers founder family life and ambition tension."],
        reference_sources=["https://example.com/founder"],
    )
    travel_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="bali travel",
            source_material=(
                "Bali travel source mentions hotels, resorts, restaurants, Ubud dinner spots, "
                "beach rituals, and honest place experience."
            ),
            target_audience="lifestyle_expat",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers Bali travel as honest place experience."],
        reference_sources=["https://example.com/travel"],
    )

    assert "жизнь предпринимателя" in founder_result.content_brief.hook_direction.lower()
    assert "wellness" not in founder_result.content_brief.hook_direction.lower()
    assert "бали" in travel_result.content_brief.hook_direction.lower()
    assert "бутик-отель" not in travel_result.content_brief.hook_direction.lower()


def test_writer_entity_keeps_same_theme_sources_distinct() -> None:
    school_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material="A founder talks about pregnancy, a child, school, and finding a Bali education decision.",
            target_audience="dreamer_woman",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers founder school decision."],
        reference_sources=["https://example.com/school"],
    )
    course_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material="A broker educator talks about students, realtors, course confidence, clients, and first deals.",
            target_audience="broker",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers broker course confidence."],
        reference_sources=["https://example.com/course"],
    )

    school_hook = school_result.content_brief.hook_direction
    course_hook = course_result.content_brief.hook_direction

    assert school_hook != course_hook
    assert any(marker in school_hook.lower() for marker in ("школ", "реб", "дет"))
    assert any(marker in course_hook.lower() for marker in ("клиент", "увер", "сдел"))


def test_workflow_b_final_content_asset_matches_review_contract() -> None:
    result = run_writer_entity_workflow(
        task=make_task(),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Clear Real Estate operates under the Zero bullshit positioning."],
        reference_sources=["https://example.com/source"],
    )

    asset = build_final_content_asset(
        writer_output=result,
        content_id="content_draft_001",
        title="Investor trust signals",
        platform="linkedin",
        pillar="expertise",
        content_format="thought_leadership_post",
        approval_status="pending",
        source_ids=["source_001"],
        insight_id="insight_001",
        idea_id=result.selected_idea.idea_id,
        brief_id="brief_001",
        draft_id="draft_001",
        edit_version_id="draft_001_edit_v1",
    )
    markdown = format_final_content_asset_markdown(asset)

    assert markdown.startswith("## Final Content Asset")
    assert "**Content ID:** content_draft_001" in markdown
    assert "**Platform:** linkedin" in markdown
    assert "**Pillar:** expertise" in markdown
    assert "**Format:** thought_leadership_post" in markdown
    assert "### Hook" not in markdown
    assert "### Final Text" in markdown
    assert asset.final_text.startswith(result.edited_final.hook)
    assert result.edited_final.hook in markdown
    assert result.edited_final.body in markdown
    assert "### CTA" not in markdown
    assert "### Traceability" not in markdown
    assert "### QA" not in markdown
    assert "- Source IDs: source_001" not in markdown
    assert "- Insight ID: insight_001" not in markdown
    assert "- Idea ID: idea_01" not in markdown
    assert "- Brief ID: brief_001" not in markdown
    assert "- Draft ID: draft_001" not in markdown
    assert "- Edit Version ID: draft_001_edit_v1" not in markdown
    assert "- Passed: True" not in markdown
    assert "- Human Review Required: True" not in markdown
    assert "Video Hooks" not in markdown
    assert "Hook Options" not in markdown


def test_workflow_b_opening_sentence_follows_quality_rules() -> None:
    result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="Про боли экспертное",
            source_material=(
                "Market report says Bali buyers often trust the first pretty villa story "
                "before checking legal structure, operator quality, and resale path."
            ),
            target_audience="developer_investor",
            platform="instagram",
            goal="authority",
            tone_of_voice="аналитический",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers Bali legal structure and operator quality."],
        reference_sources=["https://example.com/market"],
    )

    opening = result.edited_final.hook
    forbidden_starts = (
        "Сегодня поговорим о",
        "В этом посте я расскажу",
        "Давайте разберёмся",
        "Хочу поделиться",
        "Наверное, вы знаете",
        "Очень важно понимать",
        "В современном мире",
        "Сейчас многие",
    )

    assert 5 <= len(opening.split()) <= 14
    assert not any(opening.startswith(phrase) for phrase in forbidden_starts)
    assert any(marker in opening.lower() for marker in ("бали", "риск", "цен", "слой", "провер"))


def test_instagram_final_text_hides_internal_strategy_labels() -> None:
    result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material=(
                "A founder source shows the tension between ambition, family rituals, "
                "a child, and refusing to make life look perfect just for Instagram."
            ),
            target_audience="dreamer_woman",
            platform="instagram",
            goal="affinity",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers founder family life and ambition tension."],
        reference_sources=["https://example.com/founder"],
    )

    final_text = result.edited_final.body

    assert "Turn " not in final_text
    assert "The useful point" not in final_text
    assert "tension:" not in final_text
    assert "founder life" not in final_text.lower()
    assert "source" not in final_text.lower()
    assert "мотивация" not in final_text
    assert "ты" in final_text.lower()
    assert any(marker in final_text.lower() for marker in ("амбици", "сем", "жизн"))


def test_same_theme_sources_create_distinct_final_text() -> None:
    school_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material="A founder talks about pregnancy, a child, school, and finding a Bali education decision.",
            target_audience="dreamer_woman",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers founder school decision."],
        reference_sources=["https://example.com/school"],
    )
    client_result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="founder journey",
            source_material="A broker educator talks about students, realtors, course confidence, clients, and first deals.",
            target_audience="broker",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers broker course confidence."],
        reference_sources=["https://example.com/course"],
    )

    assert school_result.edited_final.body != client_result.edited_final.body
    assert any(marker in school_result.edited_final.body.lower() for marker in ("школ", "реб", "дом"))
    assert any(marker in client_result.edited_final.body.lower() for marker in ("клиент", "увер", "сдел"))


def test_linkedin_final_text_stays_english() -> None:
    result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="boutique hotels",
            source_material=(
                "A hospitality source explains that boutique hotels need operator reality, "
                "repeatable guest memory, and management discipline behind the beauty."
            ),
            target_audience="developer_investor",
            platform="linkedin",
            goal="authority",
            tone_of_voice="analytical",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers boutique hospitality operator logic."],
        reference_sources=["https://example.com/hotel"],
    )

    assert not any("а" <= char.lower() <= "я" or char.lower() == "ё" for char in result.edited_final.body)
    assert "source cue" in result.edited_final.body.lower()
    assert "operator" in result.edited_final.body.lower()


def test_video_hooks_topics_generator_applies_quality_gate() -> None:
    output = generate_video_hooks_topics(
        video_source="A villa looks affordable until the legal and operating structure is checked.",
        target_audience="developer_investor",
        platform="Instagram Reels",
        goal="retention",
        tone="sharp",
        author_profile="jane_levitan",
        n_hooks=5,
        n_topics=3,
    )

    assert len(output.top_hooks) == 5
    assert len(output.topics) == 3
    assert output.best_hook.hook_id == output.top_hooks[0].hook_id
    assert all(gate.verdict in {"keep", "rewrite", "kill"} for gate in output.hook_quality_gate)
    assert "3 tips" not in output.top_hooks[0].hook_text.lower()


def test_writer_entity_runs_jane_analyst_review_loop_before_human_review() -> None:
    result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="bali travel",
            source_material=(
                "A Bali source mentions a new Ubud restaurant, an art event, and a day-plan "
                "that works as a real island-life occasion."
            ),
            target_audience="lifestyle_expat",
            platform="instagram",
            goal="engagement",
            tone_of_voice="personal",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers a new Ubud restaurant and art event."],
        reference_sources=["https://example.com/bali-life"],
    )

    assert MAX_JANE_ANALYST_REVIEW_PASSES == 3
    assert any("Analyst review loop" in fix for fix in result.qa_report.fixes_applied)
    assert not any(issue.startswith("jane_blog_") for issue in result.qa_report.issues)
    assert any(
        marker in result.edited_final.body.lower()
        for marker in ("истори", "контекст", "деталь", "ощущ", "мест")
    )


def test_writer_entity_keeps_marketing_cases_separate_from_boutique_hotels() -> None:
    result = run_writer_entity_workflow(
        task=make_task(
            raw_topic="marketing cases",
            source_material=(
                "A real estate marketing case has reels, influencer visits, renders, and a loud launch, "
                "but cannot answer the buyer's real question: why this product, why now, and what demand proves it."
            ),
            target_audience="broker",
            platform="instagram",
            goal="authority",
            tone_of_voice="analytical",
        ),
        author_voice=build_jane_levitan_voice_object(),
        allowed_facts=["Source note covers marketing activity versus commercial proof."],
        reference_sources=["https://example.com/marketing-case"],
    )

    assert "маркетинг" in result.edited_final.hook.lower()
    assert "коммерческий сигнал" in result.edited_final.body.lower()
    assert "бутик-отель" not in result.edited_final.hook.lower()
    assert "бутик-отель" not in result.edited_final.body.lower()
