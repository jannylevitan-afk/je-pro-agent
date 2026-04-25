from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from content_engine.models.workflow_a import FilmingCard, VideoHook, VideoScript
from content_engine.n8n.payloads import (
    build_video_filming_notification,
    build_video_script_envelope,
)
from content_engine.notion.sync import (
    NotionClientLike,
    create_filming_card,
    create_script,
)


@dataclass(frozen=True, slots=True)
class VideoNotionTargets:
    scripts_database_id: str
    filming_cards_database_id: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("scripts_database_id", self.scripts_database_id),
            ("filming_cards_database_id", self.filming_cards_database_id),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class VideoGateOrchestrationResult:
    script_page_id: str
    filming_card_page_id: str
    n8n_envelope: dict[str, Any]
    telegram_notification: dict[str, Any]


def orchestrate_script_ready(
    client: NotionClientLike,
    targets: VideoNotionTargets,
    script: VideoScript,
    hook: VideoHook,
    filming_card: FilmingCard,
) -> VideoGateOrchestrationResult:
    script_response = create_script(client, targets.scripts_database_id, script)
    script_page_id = script_response["id"]

    card_response = create_filming_card(client, targets.filming_cards_database_id, filming_card)
    filming_card_page_id = card_response["id"]

    n8n_envelope = build_video_script_envelope(script, hook)
    telegram_notification = build_video_filming_notification(n8n_envelope)

    return VideoGateOrchestrationResult(
        script_page_id=script_page_id,
        filming_card_page_id=filming_card_page_id,
        n8n_envelope=n8n_envelope,
        telegram_notification=telegram_notification,
    )
