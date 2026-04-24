from pathlib import Path

from content_engine.config.fact_dossier import load_fact_dossier


def test_fact_dossier_loads_records() -> None:
    data = load_fact_dossier(Path("examples/fact_dossier.sample.yaml"))
    assert data["facts"][0]["verification_status"] == "verified_public"


def test_fact_dossier_rejects_missing_facts(tmp_path: Path) -> None:
    dossier_path = tmp_path / "bad_fact_dossier.yaml"
    dossier_path.write_text("{}\n", encoding="utf-8")

    try:
        load_fact_dossier(dossier_path)
    except ValueError as exc:
        assert "facts" in str(exc)
    else:
        raise AssertionError("Expected invalid fact dossier to fail validation")
