from content_engine.notion.schema_defs import (
    FILMING_CARDS_SCHEMA,
    SCRIPTS_QUEUE_SCHEMA,
    VIDEO_PERFORMANCE_SCHEMA,
    VIDEO_PUBLISH_CALENDAR_SCHEMA,
)


def test_scripts_queue_schema_contains_required_fields() -> None:
    assert SCRIPTS_QUEUE_SCHEMA["Title"] == "title"
    assert SCRIPTS_QUEUE_SCHEMA["Hook"] == "rich_text"
    assert SCRIPTS_QUEUE_SCHEMA["Status"] == "select"


def test_filming_cards_schema_contains_required_fields() -> None:
    assert FILMING_CARDS_SCHEMA["Linked script"] == "relation"
    assert FILMING_CARDS_SCHEMA["Raw file link"] == "url"


def test_video_publish_calendar_schema_contains_required_fields() -> None:
    assert VIDEO_PUBLISH_CALENDAR_SCHEMA["Publish date"] == "date"
    assert VIDEO_PUBLISH_CALENDAR_SCHEMA["Caption"] == "rich_text"


def test_video_performance_schema_contains_feedback_fields() -> None:
    assert VIDEO_PERFORMANCE_SCHEMA["Performance tier"] == "select"
    assert VIDEO_PERFORMANCE_SCHEMA["Fed back to RA"] == "checkbox"
