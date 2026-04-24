from content_engine.notion.schema_defs import CONTENT_PERFORMANCE_SCHEMA, RESEARCH_FEEDBACK_SIGNAL_SCHEMA


def test_content_performance_schema_contains_decision_fields() -> None:
    assert CONTENT_PERFORMANCE_SCHEMA["Linked content item"] == "relation"
    assert CONTENT_PERFORMANCE_SCHEMA["Attribution model"] == "select"
    assert CONTENT_PERFORMANCE_SCHEMA["Deal influenced"] == "checkbox"


def test_research_feedback_signal_schema_contains_priority_fields() -> None:
    assert RESEARCH_FEEDBACK_SIGNAL_SCHEMA["Signal scope"] == "select"
    assert RESEARCH_FEEDBACK_SIGNAL_SCHEMA["Signal type"] == "select"
    assert RESEARCH_FEEDBACK_SIGNAL_SCHEMA["Score"] == "number"
