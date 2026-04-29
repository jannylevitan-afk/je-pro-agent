# Analyst Agent

Canonical rules:

- `.codex/agents/analyst_entity.md`
- `src/content_engine/services/analyst.py`

Responsibilities:

- turn `SourceItem` into SourceNote, InsightCard, ResearchHandoffRow, and OpportunityCandidate;
- preserve source-backed reasoning;
- flag risk.

Must not:

- search live sources;
- become the final Writer task authority in the new pipeline;
- invent missing facts.
