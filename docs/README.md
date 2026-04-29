# Je Pro Agent Docs

This file is the documentation entrypoint for agents and humans.

## Reading Order

1. `../AGENTS.md`
2. `architecture/2026-04-29-content-factory-producer-restructure.md`
3. `architecture/2026-04-29-producer-agent-entity.md`
4. `decisions/0001-agent-first-contract.md`
5. `runbooks/validation-and-deploy.md`

## Source Of Truth Map

| Area | Current source of truth |
|---|---|
| Global agent rules | `AGENTS.md` |
| Current architecture | `docs/architecture/2026-04-29-content-factory-producer-restructure.md` |
| Producer entity | `docs/architecture/2026-04-29-producer-agent-entity.md` and `.codex/agents/producer_entity.md` |
| Analyst entity | `.codex/agents/analyst_entity.md` |
| Shared contracts | `src/content_engine/models/` |
| Service behavior | `src/content_engine/services/` plus matching `tests/services/` |
| Validation/deploy | `docs/runbooks/validation-and-deploy.md` |
| Smoke policy | `scripts/smoke/README.md` |
| Historical context | `docs/handoffs/` |

## Target Repository Structure

```text
.
├── AGENTS.md
├── .env.example
├── .github/
│   ├── agents/
│   ├── instructions/
│   └── workflows/
├── docs/
│   ├── AGENTS.md
│   ├── README.md
│   ├── architecture/
│   ├── decisions/
│   ├── handoffs/
│   └── runbooks/
├── scripts/
│   ├── AGENTS.md
│   └── smoke/
├── src/
│   ├── AGENTS.md
│   └── content_engine/
└── tests/
    └── AGENTS.md
```

## Non-Authoritative Locations

Do not treat these as source of truth:

- `outputs/`
- screenshots and images
- logs
- local downloads copied into the repo root
- `.firecrawl/`
- `.pytest_cache/`
- `.mypy_cache/`
- root-level scratch files unless a task names them explicitly

## High-Risk Files

Read tests and architecture before editing:

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

## Deploy Order

1. Contracts in `src/content_engine/models/`
2. Pure services in `src/content_engine/services/`
3. Orchestration in `src/content_engine/orchestration/`
4. Runtime or CLI entrypoints
5. Admin UI or handoff outputs

Do not wire a new model directly into `live_pipeline.py` until it has model tests,
service tests, and a dry-run path.

## Rollback Caveats

- Roll back orchestration changes before model changes.
- Do not roll back `SourceItem` fields without checking Research Agent tests.
- Do not remove compatibility fields from Writer/Analyst models until old tests and dry-run adapters are migrated.
- Never roll back by deleting unrelated dirty files.

## Completion Checklist

Run the relevant targeted test first, then:

```bash
PYTHONPATH=src:. pytest -q
python3 -m mypy src
git status --short
```

If smoke files changed:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py
```

## Docs Update Rules

When changing architecture, update `docs/architecture/`.

When changing a cross-agent rule, update `AGENTS.md` or the nearest nested
`AGENTS.md`.

When changing validation, deployment, rollback, or smoke behavior, update
`docs/runbooks/validation-and-deploy.md` or `scripts/smoke/README.md`.

When changing a long-term decision, add or update an ADR in `docs/decisions/`.
