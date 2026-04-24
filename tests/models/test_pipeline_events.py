import pytest
from pydantic import ValidationError

from content_engine.models.pipeline import PipelineEvent


def make_event(**overrides) -> dict:
    base = {
        "event_name": "source_normalized",
        "pipeline": "workflow_b",
        "entity_id": "itm_001",
        "occurred_at": "2026-04-24T09:00:00Z",
    }
    base.update(overrides)
    return base


def test_progress_event_accepted() -> None:
    event = PipelineEvent(**make_event())

    assert event.event_name == "source_normalized"
    assert event.is_failure is False
    assert event.failure_reason is None


def test_workflow_a_stage_event_accepted() -> None:
    event = PipelineEvent(**make_event(event_name="hooks_developed", pipeline="workflow_a"))

    assert event.pipeline == "workflow_a"


def test_research_agent_event_accepted() -> None:
    event = PipelineEvent(
        **make_event(event_name="routed_to_workflow_b", pipeline="research_agent")
    )

    assert event.event_name == "routed_to_workflow_b"


def test_fail_event_requires_is_failure_flag() -> None:
    with pytest.raises(ValidationError, match="is_failure"):
        PipelineEvent(**make_event(event_name="rejected_at_idea"))


def test_fail_event_requires_failure_reason() -> None:
    with pytest.raises(ValidationError, match="failure_reason"):
        PipelineEvent(
            **make_event(
                event_name="rejected_at_idea",
                is_failure=True,
            )
        )


def test_fail_event_accepted_with_all_fields() -> None:
    event = PipelineEvent(
        **make_event(
            event_name="blocked_factual_safety",
            is_failure=True,
            failure_reason="No verified claims found for all fact_claims in draft.",
        )
    )

    assert event.is_failure is True
    assert "verified" in event.failure_reason


def test_is_failure_true_on_non_fail_event_rejected() -> None:
    with pytest.raises(ValidationError, match="failure event_name"):
        PipelineEvent(
            **make_event(
                event_name="source_normalized",
                is_failure=True,
                failure_reason="something",
            )
        )


def test_all_four_fail_states_are_valid_event_names() -> None:
    fail_states = [
        "rejected_at_idea",
        "rejected_at_draft",
        "blocked_factual_safety",
        "failed_quality_gate",
    ]
    for state in fail_states:
        event = PipelineEvent(
            **make_event(
                event_name=state,
                is_failure=True,
                failure_reason=f"Triggered: {state}",
            )
        )
        assert event.event_name == state
