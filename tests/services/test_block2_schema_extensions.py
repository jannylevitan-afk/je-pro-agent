from content_engine.notion.schema_defs import (
    DISCOVERY_QUEUE_SCHEMA,
    IDEAS_DB_SCHEMA,
    INSIGHTS_DB_SCHEMA,
    MONITORING_RUN_SCHEMA,
    SOURCES_DB_SCHEMA,
)


def test_discovery_queue_schema_contains_required_fields() -> None:
    assert "Handle" in DISCOVERY_QUEUE_SCHEMA
    assert "Platform" in DISCOVERY_QUEUE_SCHEMA
    assert "Segment" in DISCOVERY_QUEUE_SCHEMA
    assert "Score" in DISCOVERY_QUEUE_SCHEMA
    assert "Why relevant" in DISCOVERY_QUEUE_SCHEMA
    assert "Approved" in DISCOVERY_QUEUE_SCHEMA
    assert "Added to monitoring" in DISCOVERY_QUEUE_SCHEMA


def test_monitoring_run_schema_contains_run_status() -> None:
    assert "Run ID" in MONITORING_RUN_SCHEMA
    assert "Connector" in MONITORING_RUN_SCHEMA
    assert "Run status" in MONITORING_RUN_SCHEMA


def test_sources_insights_ideas_schemas_exist() -> None:
    assert "Title" in SOURCES_DB_SCHEMA
    assert "Topic" in INSIGHTS_DB_SCHEMA
    assert "Platform lane" in IDEAS_DB_SCHEMA
