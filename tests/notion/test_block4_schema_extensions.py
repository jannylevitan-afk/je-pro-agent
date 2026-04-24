from content_engine.notion.schema_defs import CONTENT_CALENDAR_SCHEMA, DRAFTS_DB_SCHEMA, ORCHESTRATION_EVENT_SCHEMA


def test_drafts_schema_contains_block4_review_fields() -> None:
    assert "Platform lane" in DRAFTS_DB_SCHEMA
    assert "Language mode" in DRAFTS_DB_SCHEMA
    assert "Parent draft" in DRAFTS_DB_SCHEMA
    assert "Review requested at" in DRAFTS_DB_SCHEMA


def test_content_calendar_schema_contains_approval_metadata() -> None:
    assert "Source draft" in CONTENT_CALENDAR_SCHEMA
    assert "Approval decided at" in CONTENT_CALENDAR_SCHEMA


def test_orchestration_event_schema_exists() -> None:
    assert ORCHESTRATION_EVENT_SCHEMA["Event name"] == "select"
    assert ORCHESTRATION_EVENT_SCHEMA["Entity type"] == "select"
    assert ORCHESTRATION_EVENT_SCHEMA["Payload ref"] == "rich_text"
