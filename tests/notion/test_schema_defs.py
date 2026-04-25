from content_engine.notion.schema_defs import CONTENT_CALENDAR_SCHEMA, DRAFTS_DB_SCHEMA


def test_drafts_schema_contains_bilingual_linkedin_fields() -> None:
    assert "Draft text RU" in DRAFTS_DB_SCHEMA
    assert "Draft text EN" in DRAFTS_DB_SCHEMA
    assert "Working language" in DRAFTS_DB_SCHEMA
    assert "Publish language" in DRAFTS_DB_SCHEMA
    assert "Writer QA Report" in DRAFTS_DB_SCHEMA
    assert "Hook options" in DRAFTS_DB_SCHEMA
    assert "CTA options" in DRAFTS_DB_SCHEMA


def test_content_calendar_contains_publish_fields() -> None:
    assert "Final text RU" in CONTENT_CALENDAR_SCHEMA
    assert "Final text EN" in CONTENT_CALENDAR_SCHEMA
