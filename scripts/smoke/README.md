# Smoke Policy

Smoke scripts must be small, readable, and safe for agents to inspect quickly.

## Required Defaults

- Use a dedicated smoke user.
- Use read-only fixture entities.
- Do not mutate production data.
- Do not publish.
- Do not schedule.
- Do not charge, refund, create, update, or delete payment/acquiring entities.
- Do not scrape private or login-only sources.

## Required Environment

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent
```

Optional stable public/read-only fixtures:

```bash
CONTENT_ENGINE_SMOKE_PUBLIC_ENTITY_ID=
CONTENT_ENGINE_SMOKE_PUBLIC_INVOICE_ID=
CONTENT_ENGINE_ENABLE_DANGEROUS_SMOKE=false
```

Use `CONTENT_ENGINE_SMOKE_PUBLIC_ENTITY_ID` for stable read-only public API test
entities. Use `CONTENT_ENGINE_SMOKE_PUBLIC_INVOICE_ID` only for stable read-only
public acquiring/payment fixtures. These IDs must never point to write-enabled
production entities.

If these optional IDs are absent, smoke scripts must run contract-only checks.

## Stateful Or Dangerous Smoke

Stateful smoke must be marked in filename and docs:

```text
DANGEROUS_stateful_*.py
```

Stateful smoke is excluded from CI by default and requires
`CONTENT_ENGINE_ENABLE_DANGEROUS_SMOKE=true` plus explicit human approval.

## Current Scripts

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py
```
