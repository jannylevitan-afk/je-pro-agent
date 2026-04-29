# Copilot Instructions

Use `AGENTS.md` as the root instruction source.

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
PYTHONPATH=src:. pytest -q
python3 -m mypy src
```
