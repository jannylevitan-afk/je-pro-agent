from pathlib import Path

from content_engine.config.seed_config import load_seed_config


def test_seed_config_loads_audience_segments() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))
    assert "audience_segments" in data
    assert data["audience_segments"][0]["name"] == "developer_investor"
