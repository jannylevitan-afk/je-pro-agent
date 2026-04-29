# Je Pro Agent Operating Rules

This is the single root instruction entrypoint for agents. If another tool-specific
instruction file conflicts with this file, follow this file and then the nearest
nested `AGENTS.md` for the directory you are editing.

## Fast Reading Order

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/architecture/2026-04-29-content-factory-producer-restructure.md`
4. `docs/architecture/2026-04-29-producer-agent-entity.md`
5. `docs/decisions/0001-agent-first-contract.md`
6. `docs/runbooks/validation-and-deploy.md`

Historical handoffs, generated outputs, screenshots, logs, local downloads, and
root-level scratch files are not source of truth unless the current task names
them explicitly.

## Current Architecture Contract

Target flow:

```text
SeasonSeed / Strategy Input
  -> Producer Agent
  -> ResearchDirective[]
  -> Research Agent
  -> SourceItem + Evidence Log
  -> Analyst Entity
  -> OpportunityCandidate[]
  -> Opportunity Queue
  -> ProducerDecision / ApprovedOpportunity
  -> Brief Builder
  -> Workflow A or Workflow B
  -> Editor / QA Gate
  -> HumanReviewAsset
  -> Jane Superstar Admin Hub
```

Do not reintroduce these as active pipeline layers:

- Publisher
- Scheduler
- auto-publish
- publish queue
- visual producer
- platform variants
- format adapter
- Notion as final destination

Always use the connected MCP stack for Research Agent work when it improves fidelity:

- `exa` for source discovery, competitor expansion, founder search, and quick web research
- `firecrawl` for structured scraping, clean page extraction, and search + scrape flows
- `apify` for actor-backed collection when platform-specific extraction is needed
- `playwright` for rendered public pages, interaction-heavy pages, and browser fallback

Research Agent operating order:

1. Run compliance checks first
2. Prefer public feeds and metadata before heavier extraction
3. Require evidence fields before Workflow A or Workflow B handoff:
   - source URL
   - timestamp
   - raw excerpt
   - confidence score
4. Route signals explicitly:
   - video refs -> Workflow A
   - market/founder/text insight -> Workflow B
   - strong video plus textual depth -> both
   - weak or unsupported signal -> drop

Environment notes:

- `FIRECRAWL_API_KEY` is required for the `firecrawl` MCP server
- `APIFY_TOKEN` is required for the `apify` MCP server
- `EXA_API_KEY` is required when Exa is used with authenticated search
- `playwright` runs locally through `npx @playwright/mcp@latest`
- `ANTHROPIC_API_KEY` is required only for LLM-backed Analyst/Writer runs

Codex Analyst Instance:

- The full Analyst Entity prompt lives at `.codex/agents/analyst_entity.md`
- Launch it with `scripts/start_codex_analyst.sh`
- This is a dedicated Codex instance for Workflow B Phase 1/2 handoff, not a Python CLI product command
- Its destination is the Admin Operating Hub handoff format, not Notion

Codex Producer Entity:

- The full Producer prompt lives at `.codex/agents/producer_entity.md`
- Producer creates season logic, research directives, decisions, and brief constraints
- Producer does not search, scrape, write final copy, publish, or schedule

## High-Risk Files

Read the local code and tests before editing:

- `src/content_engine/orchestration/search_agent.py`
- `src/content_engine/orchestration/live_pipeline.py`
- `src/content_engine/services/analyst.py`
- `src/content_engine/services/producer.py`
- `src/content_engine/services/opportunity_queue.py`
- `src/content_engine/services/brief_builder.py`
- `src/content_engine/services/content_factory.py`
- `src/content_engine/services/writer_entity.py`
- `src/content_engine/models/source_item.py`
- `src/content_engine/models/producer.py`
- `src/content_engine/models/opportunity.py`
- `src/content_engine/models/brief_builder.py`
- `src/content_engine/models/content_factory.py`

## Validation Before Completion

Use the narrowest targeted test first, then full validation:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/relevant_test.py
PYTHONPATH=src:. pytest -q
python3 -m mypy src
```

If smoke policy or scripts changed, also run:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py
```

Before final handoff, run:

```bash
git status --short
```

Only stage files that belong to the current task. Do not delete or move unrelated
dirty/untracked user files without explicit instruction.
