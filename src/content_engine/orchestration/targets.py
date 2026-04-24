from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LivePipelineTargets:
    sources_database_id: str
    insights_database_id: str
    ideas_database_id: str
    briefs_database_id: str
    drafts_database_id: str
    events_database_id: str
    scripts_database_id: str
    filming_cards_database_id: str
