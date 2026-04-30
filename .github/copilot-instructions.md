# Copilot Instructions

This file is a thin adapter for GitHub Copilot. Use `AGENTS.md` as the canonical
repo-wide instruction source. If files disagree, follow `AGENTS.md`, then the
nearest nested `AGENTS.md`.

Fast reading order:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/architecture/2026-04-29-content-factory-producer-restructure.md`
4. `docs/runbooks/validation-and-deploy.md`

Respect these hard rules:

- Research Agent is the only external data collection layer.
- Producer does not search, scrape, write final copy, publish, or schedule.
- Workflow B creates one selected-platform asset, not platform variants.
- Workflow A creates hook/script/filming card, not publish queue.
- Generated outputs are not source of truth.

Before proposing completion, run or request:

```bash
make check
```
