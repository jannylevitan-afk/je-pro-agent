from pathlib import Path
from textwrap import dedent

from content_engine.config.seed_config import load_seed_config


def test_seed_config_loads_audience_segments() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))
    assert "audience_segments" in data
    assert data["audience_segments"][0]["name"] == "developer_investor"


def test_seed_config_rejects_missing_required_sections(tmp_path: Path) -> None:
    config_path = tmp_path / "bad_seed_config.yaml"
    config_path.write_text(
        dedent(
            """
            audience_segments:
              - name: developer_investor
                route_to: workflow_b
            """
        ).strip(),
        encoding="utf-8",
    )

    try:
        load_seed_config(config_path)
    except ValueError as exc:
        assert "seed_profiles" in str(exc)
    else:
        raise AssertionError("Expected invalid seed config to fail validation")
