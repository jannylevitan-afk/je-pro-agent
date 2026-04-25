from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from content_engine.collectors.http_json import fetch_source_items_from_json_feed
from content_engine.knowledge.kmd import KnowledgeStore, MarkdownKnowledgeStore
from content_engine.llm import AnthropicClient, AnthropicClientConfig, AnthropicPipelineWriter
from content_engine.models.source_item import SourceItem
from content_engine.notion import (
    NotionClient,
    NotionClientConfig,
    NotionHTTPError,
    ensure_live_pipeline_targets,
)
from content_engine.orchestration.live_pipeline import (
    LivePipelineItemResult,
    SourceCollector,
    WorkflowWriter,
    run_collector_cycle,
)
from content_engine.runtime.settings import RuntimeSettings


@dataclass(frozen=True, slots=True)
class HTTPJsonSourceCollector:
    feed_url: str
    timeout_seconds: float = 30.0

    def collect(self) -> list[SourceItem]:
        return fetch_source_items_from_json_feed(
            self.feed_url,
            timeout_seconds=self.timeout_seconds,
        )


@dataclass(frozen=True, slots=True)
class StaticSourceCollector:
    items: list[SourceItem]

    def collect(self) -> list[SourceItem]:
        return list(self.items)


def build_notion_client(settings: RuntimeSettings) -> NotionClient:
    return NotionClient(
        NotionClientConfig(
            token=settings.notion_api_key,
            base_url=settings.notion_api_base,
            notion_version=settings.notion_version,
            timeout_seconds=settings.request_timeout_seconds,
        )
    )


def build_pipeline_writer(settings: RuntimeSettings) -> AnthropicPipelineWriter:
    client = AnthropicClient(
        AnthropicClientConfig(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_api_base,
            anthropic_version=settings.anthropic_version,
            model=settings.anthropic_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
    )
    resolved_model = resolve_anthropic_model(client, settings.anthropic_model)
    return AnthropicPipelineWriter(client, model=resolved_model)


def build_source_collector(settings: RuntimeSettings) -> HTTPJsonSourceCollector:
    if not settings.source_feed_url:
        raise ValueError("CONTENT_ENGINE_SOURCE_FEED_URL must be configured for HTTP collection")
    return HTTPJsonSourceCollector(
        feed_url=settings.source_feed_url,
        timeout_seconds=settings.request_timeout_seconds,
    )


def run_configured_live_pipeline(
    *,
    settings: RuntimeSettings,
    collector: SourceCollector,
    verified_facts: set[str],
    submitted_at: str,
    notion_client: NotionClient | None = None,
    writer: WorkflowWriter | None = None,
    knowledge_store: KnowledgeStore | None = None,
) -> list[LivePipelineItemResult]:
    client = notion_client or build_notion_client(settings)
    _verify_notion_page_access(client, settings.notion_parent_page_id)
    pipeline_writer = writer or build_pipeline_writer(settings)
    targets = ensure_live_pipeline_targets(
        client=client,
        parent_page_id=settings.notion_parent_page_id,
    )
    return run_collector_cycle(
        collector=collector,
        client=client,
        targets=targets,
        verified_facts=verified_facts,
        submitted_at=submitted_at,
        writer=pipeline_writer,
        knowledge_store=knowledge_store or MarkdownKnowledgeStore(Path(settings.kmd_root)),
    )


def resolve_anthropic_model(client: AnthropicClient, requested_model: str) -> str:
    response = client.list_models()
    available_ids = [
        item.get("id")
        for item in response.get("data", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if requested_model in available_ids:
        return requested_model

    preferred_prefixes = [
        "claude-sonnet",
        "claude-opus",
    ]
    for prefix in preferred_prefixes:
        matches = [model_id for model_id in available_ids if model_id.startswith(prefix)]
        if matches:
            return matches[0]

    raise ValueError(
        "No supported Anthropic writer model is available for this API key. "
        f"Requested '{requested_model}', available: {available_ids}"
    )


def _verify_notion_page_access(client: NotionClient, page_id: str) -> None:
    try:
        client.retrieve_page(page_id)
    except NotionHTTPError as error:
        if (
            error.status_code == 404
            and isinstance(error.response_body, dict)
            and error.response_body.get("code") == "object_not_found"
            and "shared with your integration" in str(error.response_body.get("message", "")).lower()
        ):
            raise ValueError(
                "Notion page is not accessible. Please share the Notion page with the integration and try again."
            ) from error
        raise
