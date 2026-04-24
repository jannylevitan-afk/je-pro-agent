from __future__ import annotations

from dataclasses import dataclass

from content_engine.collectors.native import Fetcher, NativeSourceTarget
from content_engine.orchestration.search_agent import SearchAgentReport, run_search_agent
from content_engine.orchestration.targets import LivePipelineTargets
from content_engine.runtime.dry_run import InMemoryNotionClient
from content_engine.orchestration.live_pipeline import WorkflowWriter


_LOCAL_TARGETS = LivePipelineTargets(
    sources_database_id="db_sources",
    insights_database_id="db_insights",
    ideas_database_id="db_ideas",
    briefs_database_id="db_briefs",
    drafts_database_id="db_drafts",
    events_database_id="db_events",
    scripts_database_id="db_scripts",
    filming_cards_database_id="db_filming",
)


@dataclass(frozen=True, slots=True)
class LocalSearchAgentDryRunReport:
    search_report: SearchAgentReport
    database_snapshots: dict[str, list[dict]]


def run_local_search_agent_dry_run(
    *,
    search_targets: list[NativeSourceTarget],
    writer: WorkflowWriter | None,
    verified_facts: set[str],
    submitted_at: str,
    timeout_seconds: float = 30.0,
    fetcher: Fetcher | None = None,
    collected_at: str | None = None,
) -> LocalSearchAgentDryRunReport:
    client = InMemoryNotionClient()
    search_report = run_search_agent(
        client=client,
        targets=_LOCAL_TARGETS,
        search_targets=search_targets,
        verified_facts=verified_facts,
        submitted_at=submitted_at,
        writer=writer,
        timeout_seconds=timeout_seconds,
        fetcher=fetcher,
        collected_at=collected_at,
    )
    return LocalSearchAgentDryRunReport(
        search_report=search_report,
        database_snapshots=client.snapshot(),
    )
