# Database And Migrations Instructions

Canonical docs:

- `AGENTS.md`
- `docs/README.md`
- `docs/runbooks/validation-and-deploy.md`

Applies to future database paths:

- `db/**`
- `migrations/**`
- `alembic/**`
- `supabase/**`

Current state:

- This repo has no active database migration system.
- Do not introduce one without an ADR in `docs/decisions/`.

Local invariants if migrations are added:

- Every migration needs rollback notes.
- Destructive migrations require a runbook and explicit human approval.
- Migrations must be deterministic and safe to run in CI against a disposable DB.
- Generated migration artifacts must not become architecture source of truth.

Validation:

```bash
make check
```

Add a migration-specific smoke command before enabling production deploy.
