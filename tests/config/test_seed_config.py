from pathlib import Path
from textwrap import dedent

from content_engine.config.seed_config import (
    build_discovery_queries,
    build_native_source_targets,
    load_seed_config,
)


def test_seed_config_loads_audience_segments() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))
    assert "audience_segments" in data
    assert data["audience_segments"][0]["name"] == "developer_investor"


def test_seed_config_saves_blog_source_pool_with_collection_rules() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))
    themes = {theme["name"]: theme for theme in data["content_theme_sources"]}

    assert themes["founder_journey"]["sources"][0]["source_url"] == "https://www.instagram.com/annalutaeva/"
    assert "family/business tension" in themes["founder_journey"]["collect_fields"]
    assert "founder story" in themes["founder_journey"]["discovery_keywords"]
    assert themes["expert_pain_bali"]["sources"][0]["source_url"] == "https://t.me/Bali_expert"
    assert themes["bali_travel"]["route_to"] == "both"
    assert themes["global_trends"]["sources"][0]["source_url"].startswith("https://www.htrends.com/")
    assert themes["boutique_hotels"]["sources"][-1]["source_url"] == "https://www.wallpaper.com/"


def test_build_native_source_targets_from_seed_config() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))

    targets = build_native_source_targets(data)

    assert len(targets) >= 24
    assert targets[0].platform == "instagram"
    assert targets[0].handle == "annalutaeva"
    assert targets[0].audience_segment == "dreamer_woman"
    assert targets[0].content_theme == "founder_journey"
    assert targets[0].source_name == "Anna Lutaeva"
    assert any(target.source_url == "https://www.dezeen.com/" for target in targets)


def test_build_discovery_queries_from_seed_themes() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))

    queries = build_discovery_queries(data)

    assert any(
        query.content_theme == "boutique_hotels"
        and query.platform_target == "instagram hospitality pages"
        and "boutique hotel design" in query.query
        for query in queries
    )
    assert any(
        query.content_theme == "founder_journey"
        and query.audience_segment == "dreamer_woman"
        and "founder story" in query.query
        for query in queries
    )


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
