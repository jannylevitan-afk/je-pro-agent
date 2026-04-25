from content_engine.models.writer_entity import AvailableContext, WriterTaskInput
from content_engine.services.writer_entity import (
    build_jane_levitan_voice_object,
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
