# Backend Instructions

Canonical docs:

- `AGENTS.md`
- `docs/README.md`
- `docs/architecture/2026-04-29-content-factory-producer-restructure.md`
- `docs/runbooks/validation-and-deploy.md`

Applies to:

- `src/content_engine/**`
- `tests/models/**`
- `tests/services/**`
- `tests/orchestration/**`
- `tests/runtime/**`

Local invariants:

- Keep shared data shapes in `src/content_engine/models/`.
- Keep deterministic behavior in `src/content_engine/services/`.
- Keep external collection in Research Agent / collector adapters only.
- Do not add publishing, scheduling, or auto-publish paths.
- Do not add secrets to code, tests, docs, or fixtures.

Validation:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/relevant_test.py
make check
```
