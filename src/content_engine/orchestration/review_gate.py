from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from content_engine.models.approval import ApprovalResult
from content_engine.n8n.payloads import (
    build_review_gate_envelope,
    build_telegram_notification_payload,
)
from content_engine.notion.sync import (
    ApprovalNotionTargets,
    ApprovalSyncResult,
    NotionClientLike,
    sync_approval_result,
)


@dataclass(frozen=True, slots=True)
class ReviewGateOrchestrationResult:
    notion_sync: ApprovalSyncResult
    n8n_envelope: dict[str, Any]
    telegram_notification: dict[str, Any]


def orchestrate_review_outcome(
    client: NotionClientLike,
    targets: ApprovalNotionTargets,
    result: ApprovalResult,
) -> ReviewGateOrchestrationResult:
    notion_sync = sync_approval_result(
        client=client,
        targets=targets,
        result=result,
    )
    n8n_envelope = build_review_gate_envelope(result)
    telegram_notification = build_telegram_notification_payload(n8n_envelope)
    return ReviewGateOrchestrationResult(
        notion_sync=notion_sync,
        n8n_envelope=n8n_envelope,
        telegram_notification=telegram_notification,
    )
