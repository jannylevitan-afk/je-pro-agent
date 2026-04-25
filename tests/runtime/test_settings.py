from pathlib import Path

from content_engine.runtime.settings import RuntimeSettings, load_runtime_settings


def test_load_runtime_settings_prefers_explicit_environment_over_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "\n".join(
            [
                "NOTION_API_KEY=file-notion-token",
                "NOTION_PARENT_PAGE_URL=https://www.notion.so/workspace/Content-fabric-34b2a925815780b8bd08d56c7e1293cf",
                "ANTHROPIC_API_KEY=file-anthropic-token",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_runtime_settings(
        environ={
            "NOTION_API_KEY": "env-notion-token",
            "NOTION_PARENT_PAGE_URL": "https://www.notion.so/workspace/Other-page-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "ANTHROPIC_API_KEY": "env-anthropic-token",
            "ANTHROPIC_MODEL": "claude-opus-4-20250514",
            "CONTENT_ENGINE_KMD_ROOT": "tmp/kmd",
            "N8N_WEBHOOK_URL": "https://n8n.example/webhook/video",
        },
        env_file=env_file,
    )

    assert settings.notion_api_key == "env-notion-token"
    assert settings.anthropic_api_key == "env-anthropic-token"
    assert settings.anthropic_model == "claude-opus-4-20250514"
    assert settings.notion_parent_page_id == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert settings.kmd_root == "tmp/kmd"
    assert settings.n8n_webhook_url == "https://n8n.example/webhook/video"


def test_load_runtime_settings_reads_env_file_when_process_env_missing(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "\n".join(
            [
                "NOTION_API_KEY=file-notion-token",
                "NOTION_PARENT_PAGE_URL=https://www.notion.so/detoxcourse/Content-fabric-34b2a925815780b8bd08d56c7e1293cf?showMoveTo=true",
                "ANTHROPIC_API_KEY=file-anthropic-token",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_runtime_settings(environ={}, env_file=env_file)

    assert settings.notion_api_key == "file-notion-token"
    assert settings.anthropic_api_key == "file-anthropic-token"
    assert settings.anthropic_model == "claude-sonnet-4-20250514"
    assert settings.notion_parent_page_id == "34b2a925-8157-80b8-bd08-d56c7e1293cf"
    assert settings.kmd_root == "knowledge/kmd"
    assert settings.n8n_webhook_url is None


def test_runtime_settings_accepts_explicit_page_id_without_url() -> None:
    settings = RuntimeSettings(
        notion_api_key="notion-token",
        notion_parent_page_id="34b2a925815780b8bd08d56c7e1293cf",
        anthropic_api_key="anthropic-token",
    )

    assert settings.notion_parent_page_id == "34b2a925-8157-80b8-bd08-d56c7e1293cf"
    assert settings.notion_parent_page_url is None
