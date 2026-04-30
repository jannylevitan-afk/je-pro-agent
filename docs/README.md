# Je Pro Agent Docs

This file is the documentation entrypoint for agents and humans.

## Reading Order

1. `../AGENTS.md`
2. `architecture/2026-04-29-content-factory-producer-restructure.md`
3. `architecture/2026-04-29-producer-agent-entity.md`
4. `decisions/0001-agent-first-contract.md`
5. `runbooks/validation-and-deploy.md`
6. `scripts/smoke/README.md` when smoke or remote validation is involved

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
| Incidents and hidden constraints | `docs/incidents/` |
| Active handoffs | `docs/tasks/active/` |
| Historical plans | `docs/plans/` and `docs/superpowers/plans/` |
| External research | `docs/research/` |

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
│   ├── incidents/
│   ├── plans/
│   ├── research/
│   ├── tasks/
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
- local imported context files ignored by `.gitignore` until durable material is
  promoted into `docs/`

Durable knowledge cannot remain only in chat. If a conversation establishes a
lasting rule, hidden constraint, incident, or process decision, write it into the
folder below before final handoff.

## Placement Rules

| Knowledge type | Put it here | Rule |
|---|---|---|
| Current system behavior | `docs/architecture/` | Use dated files; update this README when current file changes |
| Validation/deploy/debug procedure | `docs/runbooks/` | Include exact commands and rollback caveats |
| Durable decision or process rule | `docs/decisions/` | Use ADR format with status/date/consequences |
| Regression or hidden constraint | `docs/incidents/` | Include symptom, cause, fix, prevention |
| Temporary active handoff | `docs/tasks/active/` | Include owner/status/next command; remove or archive when done |
| Historical plan/design | `docs/plans/` | Mark historical; do not override current architecture |
| External research | `docs/research/` | Include source URLs and date |
| Generated output | `outputs/` | Never use as source of truth |

## Newly Imported Context

The following imported root documents were promoted into durable folders on
2026-04-30:

- `docs/plans/2026-04-30-codex-content-factory-restructure-source-spec-ru.md`
- `docs/plans/2026-04-30-producer-agent-source-spec-ru.md`
- `docs/plans/2026-04-30-workflow-b-final-output-contract-source-spec.md`
- `docs/research/2026-04-30-saas-open-source-production-architecture.md`

They are context inputs, not replacements for current architecture.

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
make check
git status --short
```

If smoke files changed:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts
```

## Docs Update Rules

When changing architecture, update `docs/architecture/`.

When changing a cross-agent rule, update `AGENTS.md` or the nearest nested
`AGENTS.md`.

When changing validation, deployment, rollback, or smoke behavior, update
`docs/runbooks/validation-and-deploy.md` or `scripts/smoke/README.md`.

When changing a long-term decision, add or update an ADR in `docs/decisions/`.
