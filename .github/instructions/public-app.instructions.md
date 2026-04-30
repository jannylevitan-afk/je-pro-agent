# Public App Instructions

Canonical docs:

- `AGENTS.md`
- `docs/README.md`
- `docs/runbooks/validation-and-deploy.md`

Applies to future public app paths:

- `apps/public/**`
- `public-app/**`
- `src/content_engine/runtime/**`

Local invariants:

- Public flows are read-only unless a runbook explicitly marks them stateful.
- Do not expose internal source evidence, private notes, API keys, or debug traces.
- Auth/card/public smoke must be separate and read-only by default.
- If remote smoke env is missing, skip instead of guessing.

Validation:

```bash
make check
CONTENT_ENGINE_SMOKE_MODE=readonly CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
  PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow public
```
