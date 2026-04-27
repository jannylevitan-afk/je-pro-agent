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


def test_codex_analyst_instance_includes_strategy_voice_and_fact_context() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    required_sources = [
        "Стратегия AI агент Instagram LinkedIn.docx",
        "Voice_Jane_Levitan_Agent.md",
        "Fact_Dossier_Jane_Levitan_RU.md",
        "target-audience-portraits.md",
        "content_farm_workflow_spec.md",
        "writer_entity_combined_technical_spec.md",
    ]

    for source in required_sources:
        assert source in prompt

    assert "Strategic Editorial Rules" in prompt
    assert "Voice, Audience, And Fact Fit" in prompt
    assert "Jane Voice Register Map" in prompt
    assert "Fact & Privacy Boundaries" in prompt


def test_codex_analyst_instance_passes_editorial_strategy_to_writer_tz() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    assert "rental yield over flipping" in prompt
    assert "front-loaded payments" in prompt
    assert "AILLA is a cross-cutting flagship narrative" in prompt
    assert "Lifestyle and women-focused content is valuable in itself" in prompt
    assert "Professional real estate claims must come from source material" in prompt
    assert "Primary Jane register" in prompt
    assert "Tone to avoid" in prompt
    assert "Claims to avoid" in prompt


def test_codex_analyst_instance_defines_writer_assignment_outcome_contract() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    assert "Writer Assignment Outcome Document" in prompt
    assert "Required Asset Matrix" in prompt
    assert "Missing Theme Inputs" in prompt
    assert "Writer Assignment ID" in prompt
    assert "Produce one assignment per approved theme/platform lane" in prompt

    required_lane_pairs = [
        "founder_journey / instagram_lifestyle",
        "expert_pain_bali / instagram_professional",
        "expert_pain_bali / linkedin_b2b",
        "land_and_legal / instagram_professional",
        "land_and_legal / linkedin_b2b",
        "market_reports / instagram_professional",
        "market_reports / linkedin_b2b",
        "bali_travel / instagram_lifestyle",
        "global_trends / instagram_professional",
        "global_trends / linkedin_b2b",
        "wellness_architecture / instagram_lifestyle",
        "wellness_architecture / instagram_professional",
        "wellness_architecture / linkedin_b2b",
        "boutique_hotels / instagram_professional",
        "boutique_hotels / linkedin_b2b",
        "marketing_cases / instagram_professional",
        "marketing_cases / linkedin_b2b",
    ]

    for lane_pair in required_lane_pairs:
        assert lane_pair in prompt


def test_codex_analyst_instance_includes_workflow_a_video_source_context_boundary() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    required_phrases = [
        "Workflow A Video Source Context",
        "Video refs",
        "First 3 seconds / source hook",
        "Hook pattern",
        "Tension",
        "Promise",
        "Visual device",
        "Repeatable formula",
        "Public comments / reactions",
        "Workflow A boundary",
    ]

    for phrase in required_phrases:
        assert phrase in prompt
