# ADR 0001: Agent-First Repository Contract

**Status:** Accepted  
**Date:** 2026-04-29

## Context

The project is built by multiple AI agents and humans over many sessions. The repo
already has historical handoffs, generated outputs, local scratch files, and several
entity-specific prompts. Without a strict navigation contract, agents can follow old
or conflicting instructions.

## Decision

Use an agent-first repository contract:

- `AGENTS.md` is the root instruction entrypoint.
- Nested `AGENTS.md` files may only narrow local rules.
- `docs/README.md` defines reading order and source-of-truth mapping.
- Durable process rules live in `docs/decisions/` or `docs/runbooks/`.
- Regressions and hidden constraints live in `docs/incidents/`.
- Temporary active handoffs live in `docs/tasks/active/`.
- Historical plans live in `docs/plans/`.
- External research lives in `docs/research/`.
- Shared data contracts live in `src/content_engine/models/`.
- Deterministic behavior lives in `src/content_engine/services/`.
- Generated outputs, logs, screenshots, caches, and root scratch files are not source of truth.
- Tool-specific docs stay thin and link back to canonical docs.
- `make check` is the repo-wide deterministic validation contract.

## Consequences

- Agents can start work with a small reading set.
- Historical docs remain useful without overriding current rules.
- Validation is deterministic and repeatable.
- Durable knowledge does not disappear into chat history.
- Smoke scripts are safe by default.
- Production changes are safer because high-risk files and rollback caveats are explicit.

## Non-Goals

- This ADR does not remove existing historical files.
- This ADR does not add publishing, scheduling, or live production smoke mutations.
