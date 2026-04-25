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
