from content_engine.notion.schema_defs import DISCOVERY_QUEUE_SCHEMA, MONITORING_RUN_SCHEMA


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
