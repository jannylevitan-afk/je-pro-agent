from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SEASON_DIR = ROOT / "docs" / "seasons" / "2026-04-jane-health-villa"


def test_current_jane_season_workspace_exists() -> None:
    required_paths = [
        ROOT / "docs" / "seasons" / "README.md",
        ROOT / "docs" / "seasons" / "AGENTS.md",
        SEASON_DIR / "README.md",
        SEASON_DIR / "producer-output.md",
        SEASON_DIR / "research-directives.md",
    ]

    for path in required_paths:
        assert path.exists(), f"missing season workspace file: {path.relative_to(ROOT)}"


def test_current_jane_producer_output_is_human_facing_contract() -> None:
    producer_output = (SEASON_DIR / "producer-output.md").read_text(encoding="utf-8")

    required_sections = [
        "# Продюсерский итоговый документ",
        "## Продюсерский бриф",
        "## Библия сезона",
        "## Контентные линии",
        "## Карточки сцен",
        "## Задачи для рабочих сущностей",
        "## Финальная продюсерская сборка",
        "## Что сделать первым",
    ]

    for section in required_sections:
        assert section in producer_output


def test_current_jane_research_directives_are_search_agent_source_of_truth() -> None:
    directives = (SEASON_DIR / "research-directives.md").read_text(encoding="utf-8")

    required_phrases = [
        "Search Agent must read this file before Workflow A hook research",
        "source_count_target: 50",
        "platform_source_targets:",
        "youtube: 15",
        "tiktok: 15",
        "instagram: 20",
        "language_source_targets:",
        "ru: 25",
        "en: 25",
        "topic_search_order:",
        "per_topic_platform_targets:",
        "youtube: 3",
        "tiktok: 3",
        "instagram: 4",
        "topic_source_targets:",
        "recovery_energy: 10",
        "invisible_quality: 10",
        "bali_real_estate: 10",
        "phygital_villa_experience: 10",
        "founder_ceo_transition: 10",
        "audience_participation is a CTA/feedback mechanic",
        "Search each topic sequentially until its qualified count is met",
        "Search both Russian and English public videos",
        "use Firecrawl CLI/API outside the MCP path",
        "Use Apify actor-backed extraction for Instagram Reels and TikTok public videos",
        "qualified_topic_counts must match topic_source_targets",
    ]

    for phrase in required_phrases:
        assert phrase in directives


def test_docs_reading_order_promotes_season_workspace_over_outputs() -> None:
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    root_agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "docs/seasons/" in docs_readme
    assert "docs/seasons/2026-04-jane-health-villa/research-directives.md" in docs_readme
    assert "Season Workspace" in root_agents
    assert "outputs/2026-04-30_jane_health_villa_producer_output.md" not in docs_readme
