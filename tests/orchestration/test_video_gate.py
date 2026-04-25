import pytest

from content_engine.models.workflow_a import FilmingCard, VideoScript
from content_engine.orchestration.video_gate import (
    VideoGateOrchestrationResult,
    VideoNotionTargets,
    orchestrate_script_ready,
)
from tests.notion.conftest import StubNotionClient


def make_script() -> VideoScript:
    return VideoScript(
        script_id="scr_hook_001_1",
        source_item_id="itm_vid_001",
        title="Boutique Hotels signal for developer_investor",
        platform="instagram",
        hook_text="What looks cheap first is often the most expensive later.",
        script_text="Hook\nLesson\nCTA",
        cta="Save this for the next deal review.",
        filming_priority=1,
        status="scripted",
    )


def make_filming_card() -> FilmingCard:
    return FilmingCard(
        card_id="film_scr_hook_001_1",
        linked_script_id="scr_hook_001_1",
        filming_priority=1,
        filmed=False,
    )


def test_orchestrate_script_ready_creates_notion_entries(video_hook) -> None:
    client = StubNotionClient(
        create_results=[{"id": "page_script_001"}, {"id": "page_film_001"}],
    )
    targets = VideoNotionTargets(
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    result = orchestrate_script_ready(
        client=client,
        targets=targets,
        script=make_script(),
        hook=video_hook,
        filming_card=make_filming_card(),
    )

    assert isinstance(result, VideoGateOrchestrationResult)
    assert result.script_page_id == "page_script_001"
    assert result.filming_card_page_id == "page_film_001"
    assert len(client.create_calls) == 2


def test_orchestrate_script_ready_builds_n8n_envelope(video_hook) -> None:
    client = StubNotionClient(
        create_results=[{"id": "page_script_001"}, {"id": "page_film_001"}],
    )
    targets = VideoNotionTargets(
        scripts_database_id="db_scripts",
        filming_cards_database_id="db_filming",
    )

    result = orchestrate_script_ready(
        client=client,
        targets=targets,
        script=make_script(),
        hook=video_hook,
        filming_card=make_filming_card(),
    )

    assert result.n8n_envelope["workflow"] == "video_pipeline"
    assert result.n8n_envelope["route"] == "script_ready"
    assert result.telegram_notification["channel"] == "telegram"
    assert "priority 1" in result.telegram_notification["message"]


def test_video_notion_targets_rejects_empty_ids() -> None:
    with pytest.raises(ValueError, match="scripts_database_id"):
        VideoNotionTargets(scripts_database_id="", filming_cards_database_id="db_filming")
