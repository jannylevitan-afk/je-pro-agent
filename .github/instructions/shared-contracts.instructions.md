# Shared Contracts Instructions

Canonical docs:

- `AGENTS.md`
- `docs/README.md`
- `docs/decisions/0001-agent-first-contract.md`

Applies to:

- `src/content_engine/models/**`
- `tests/models/**`
- contract fixtures in `examples/**`

Local invariants:

- Models are the shared language between agents.
- Add or update model tests for every contract change.
- Do not remove compatibility fields until services, tests, and generated outputs
  no longer use them.
- Prefer explicit literal values over loose strings when routing or workflow state
  affects behavior.

Validation:

```bash
PYTHONPATH=src:. pytest -q tests/models
make check
```
