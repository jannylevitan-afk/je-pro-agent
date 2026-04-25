from content_engine.models.writer_entity import (
    AvailableContext,
    WriterTaskInput,
)


def test_writer_task_input_keeps_required_context_flags() -> None:
    task = WriterTaskInput(
        raw_topic="Bali market risk",
        source_material="A source note about deal structure and buyer risk.",
        target_audience="developer_investor",
        platform="linkedin",
        goal="authority",
        tone_of_voice="analytical",
        length="medium",
        cta_type="comment",
        author_profile="jane_levitan",
        available_context=AvailableContext(
            fact_dossier=True,
            voice_profile=True,
            source_material=True,
        ),
    )

    assert task.author_profile == "jane_levitan"
    assert task.available_context.fact_dossier is True
