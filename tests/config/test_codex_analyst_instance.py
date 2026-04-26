from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / ".codex" / "agents" / "analyst_entity.md"


def test_codex_analyst_instance_includes_required_theme_matrix() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    required_themes = [
        "founder_journey",
        "expert_pain_bali",
        "land_and_legal",
        "market_reports",
        "bali_travel",
        "global_trends",
        "wellness_architecture",
        "boutique_hotels",
        "marketing_cases",
    ]

    for theme in required_themes:
        assert theme in prompt


def test_codex_analyst_instance_requires_all_workflow_b_lanes() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    assert "instagram_lifestyle" in prompt
    assert "instagram_professional" in prompt
    assert "linkedin_b2b" in prompt
    assert "Produce one Writer Entity TZ per required Workflow B platform lane" in prompt
    assert "Theme Coverage Checklist" in prompt
