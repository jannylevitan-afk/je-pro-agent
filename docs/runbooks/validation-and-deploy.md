# Validation And Deploy Runbook

## Purpose

Use this runbook before declaring a task complete, before pushing code, and before
deploying any production-facing change.

## Local Validation

Run the narrowest relevant test first:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/test_file.py
```

Then run full validation:

```bash
make check
```

If smoke files changed:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts
```

`make check` runs:

1. Python compile check for `src` and `tests`.
2. Read-only contract smoke.
3. Full pytest suite.
4. mypy over `src`.

## Deploy Order

1. Models and schemas.
2. Pure services.
3. Dry-run orchestration.
4. Live orchestration.
5. Runtime/CLI entrypoints.
6. Admin UI or generated handoff outputs.

Do not deploy step 4 before step 3 has deterministic tests.

## Rollback Order

1. Disable new runtime entrypoint or feature flag.
2. Roll back orchestration call site.
3. Keep models temporarily if old data may still reference them.
4. Remove compatibility fields only after tests and generated outputs no longer need them.

## High-Risk Change Checklist

For changes to Research, Analyst, Producer, Brief Builder, Writer, or live orchestration:

- Confirm Research Agent remains the only collection layer.
- Confirm no publisher/scheduler/auto-publish path was introduced.
- Confirm source evidence fields remain available.
- Confirm Workflow B does not emit platform variants.
- Confirm Workflow A does not emit publish queue in the new pipeline.
- Confirm human-review outputs are not marked published or scheduled.

## Remote Smoke

Remote smoke is optional and read-only by default. It must use only GitHub
repository variables and secrets.

Required repository variables:

- `CONTENT_ENGINE_REMOTE_SMOKE_BASE_URL`
- `CONTENT_ENGINE_SMOKE_USER_ID`
- `CONTENT_ENGINE_SMOKE_AUTH_USER_ID` for auth smoke
- `CONTENT_ENGINE_SMOKE_PUBLIC_CARD_ID` for card smoke
- `CONTENT_ENGINE_SMOKE_PUBLIC_ENTITY_ID` for public API smoke
- `CONTENT_ENGINE_SMOKE_PUBLIC_INVOICE_ID` for public acquiring/API smoke

Required repository secret:

- `CONTENT_ENGINE_REMOTE_SMOKE_TOKEN`

If a job-specific value is missing, `.github/workflows/remote-smoke.yml` skips
that job instead of guessing.

## Git Handoff

Before commit:

```bash
git status --short
git diff --stat
git diff --cached --stat
```

Stage only task-owned files.

Do not remove unrelated dirty or untracked user files.
