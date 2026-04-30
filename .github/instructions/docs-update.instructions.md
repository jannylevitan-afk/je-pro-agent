# Docs Update Instructions

When changing architecture, update `docs/architecture/` and `docs/README.md`.

When changing process rules, update `AGENTS.md`, a nested `AGENTS.md`, an ADR, or a runbook.

When changing validation or deploy commands, update `docs/runbooks/validation-and-deploy.md`.

When changing smoke behavior, update `scripts/smoke/README.md`.

When discovering a hidden constraint or regression, add a note to
`docs/incidents/`.

When a task needs low-context handoff, use `docs/tasks/active/` and remove or
archive the note when the task finishes.

Do not bury durable rules only in historical handoffs.
