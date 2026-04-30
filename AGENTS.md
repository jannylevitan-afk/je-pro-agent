# Je Pro Agent Operating Rules

This is the single root instruction entrypoint for agents. If another tool-specific
instruction file conflicts with this file, follow this file and then the nearest
nested `AGENTS.md` for the directory you are editing.

Nearest `AGENTS.md` wins for its subtree. Tool-specific files such as
`CLAUDE.md`, `.github/copilot-instructions.md`, `.github/instructions/*`, and
`.github/agents/*` are compatibility adapters. They must link back here and must
not become a second source of truth.

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

Durable knowledge cannot live only in chat. If a session discovers a lasting
constraint, regression, decision, or operator procedure, write it to `docs/`.

## Repository Map

| Path | Purpose |
|---|---|
| `.codex/agents/` | Full local prompts for dedicated Codex entities |
| `.agents/skills/` | Local Research Agent skills |
| `.github/agents/` | Thin GitHub-native role adapters |
| `.github/instructions/` | Thin path-specific GitHub guidance |
| `.github/workflows/` | CI, setup, and optional smoke automation |
| `docs/architecture/` | Current architecture and dated architecture replacements |
| `docs/runbooks/` | Validation, deploy, rollback, debug, ops |
| `docs/decisions/` | ADRs and durable process decisions |
| `docs/incidents/` | Regressions, hidden constraints, postmortems |
| `docs/tasks/active/` | Temporary handoff notes for active work only |
| `docs/plans/` | Historical design context and old plans |
| `docs/research/` | External research and source analysis |
| `examples/` | Safe sample inputs and seed configs |
| `knowledge/kmd/` | Generated knowledge material for agent handoff |
| `outputs/` | Generated local outputs, never source of truth |
| `scripts/` | Small operational scripts |
| `src/content_engine/` | Python package |
| `tests/` | Deterministic tests mirroring package areas |

## Main Packages And Applications

- `src/content_engine/models/`: shared contracts. Change these first when the data shape changes.
- `src/content_engine/services/`: deterministic business behavior. Keep external I/O out unless the service is explicitly an adapter.
- `src/content_engine/orchestration/`: connects services into flows. Treat as high-risk.
- `src/content_engine/runtime/` and `src/content_engine/cli/`: executable entrypoints.
- `src/content_engine/collectors/`, `llm/`, `notion/`, `n8n/`: integration adapters. Keep secrets in env, not code.
- There is no active frontend app yet. Future admin/public apps must add local `AGENTS.md` only if their rules differ from this file.

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

## Universal Commands

Use these from the repo root:

```bash
make check
make test
make typecheck
bash scripts/check.sh
CONTENT_ENGINE_SMOKE_MODE=readonly CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
  PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts
```

`make check` and `bash scripts/check.sh` are the repo-wide validation contract.

## Global Invariants

- Research Agent is the only layer that collects external data.
- Compliance and evidence logging happen before Workflow A or Workflow B handoff.
- Producer orchestrates season logic and decisions; it does not search, scrape, write, publish, or schedule.
- Analyst structures source-backed insights; it does not invent facts or collect live sources.
- Writer writes from approved briefs; it does not become a search agent.
- Workflow B returns one selected-platform asset, not platform variants.
- Workflow A returns video hook/script/filming-ready material, not an automatic publisher.
- Admin Operating Hub is the intended output layer; Notion is not the current destination.
- Generated outputs, cache folders, screenshots, logs, dist/build files, and root scratch files are not source of truth.

## Validation Before Completion

Use the narrowest targeted test first, then full validation:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/relevant_test.py
make check
```

If smoke policy or scripts changed, also run:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
  PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts
```

Before final handoff, run:

```bash
git status --short
```

Only stage files that belong to the current task. Do not delete or move unrelated
dirty/untracked user files without explicit instruction.

## Update Obligations

- Architecture behavior changed -> update `docs/architecture/` and `docs/README.md`.
- Validation, deploy, smoke, or rollback changed -> update `docs/runbooks/validation-and-deploy.md` or `scripts/smoke/README.md`.
- Durable rule changed -> add or update an ADR in `docs/decisions/`.
- Regression or hidden constraint found -> add an incident note in `docs/incidents/`.
- Active handoff needed -> use `docs/tasks/active/` and delete/archive it when done.
- External research used as design input -> place it in `docs/research/`.
