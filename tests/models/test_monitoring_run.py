from content_engine.models.monitoring import MonitoringRun


def test_monitoring_run_accepts_operational_fields() -> None:
    run = MonitoringRun(
        run_id="run_001",
        connector="instagram",
        source_name="@clear_real_estate",
        started_at="2026-04-24T08:00:00Z",
        finished_at="2026-04-24T08:05:00Z",
        fetched_count=12,
        failed_count=1,
        last_success_at="2026-04-24T08:05:00Z",
        error_type="rate_limit",
        retry_count=2,
        staleness_hours=4,
        run_status="partial",
    )

    assert run.run_status == "partial"
    assert run.retry_count == 2


def test_monitoring_run_rejects_invalid_status() -> None:
    try:
        MonitoringRun(
            run_id="run_001",
            connector="instagram",
            source_name="@clear_real_estate",
            started_at="2026-04-24T08:00:00Z",
            finished_at="2026-04-24T08:05:00Z",
            fetched_count=12,
            failed_count=1,
            last_success_at="2026-04-24T08:05:00Z",
            error_type="rate_limit",
            retry_count=2,
            staleness_hours=4,
            run_status="unknown",
        )
    except ValueError:
        assert True
    else:
        raise AssertionError("Expected invalid run status to fail")
