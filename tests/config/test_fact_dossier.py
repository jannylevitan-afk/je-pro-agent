from pathlib import Path

from content_engine.config.fact_dossier import load_fact_dossier


def test_fact_dossier_loads_records() -> None:
    data = load_fact_dossier(Path("examples/fact_dossier.sample.yaml"))
    assert data["facts"][0]["verification_status"] == "verified_public"
