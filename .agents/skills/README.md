# Je Pro Research Agent Skill Pack

These project-local skills wrap the Research Agent logic described in
`content_engine_architecture_v3.md` into reusable operating instructions.

## Skill Stack

- `research-agent-runner` — orchestrates the full Layer 0 flow
- `analyst-entity-runner` — runs Workflow B Analyst Entity from CLI and emits Writer TZ
- `source-discovery-skill` — finds and expands source pools
- `video-intake-skill` — captures video-first raw material for Workflow A
- `hook-mining-skill` — extracts reusable hook formulas
- `insight-extraction-skill` — turns raw text into structured insight cards
- `routing-skill` — sends signals to Workflow A, Workflow B, both, or drop
- `evidence-log-skill` — blocks unsupported insights from reaching Notion
- `compliance-gate-skill` — enforces public-source and data-minimization rules

## Code Mapping

- Collection: `src/content_engine/collectors/native.py`
- Search Agent orchestration: `src/content_engine/orchestration/search_agent.py`
- Workflow routing: `src/content_engine/services/routing.py`
- Analyst Entity CLI: `src/content_engine/cli/analyst.py`
- Workflow A primitives: `src/content_engine/services/workflow_a.py`
- Workflow B primitives: `src/content_engine/services/workflow_b.py`
- Local dry run: `src/content_engine/runtime/search_dry_run.py`

## MCP Mapping

- `exa` — discovery, related-source expansion, founder and company lookup
- `firecrawl` — structured search and scrape on public web pages
- `apify` — actor-backed platform extraction when simple page parsing is not enough
- `playwright` — rendered-page and interaction fallback

Required env vars for the currently configured MCP stack:

- `FIRECRAWL_API_KEY`
- `APIFY_TOKEN`
