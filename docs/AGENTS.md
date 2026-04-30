# Docs Directory Rules

`docs/README.md` is the docs entrypoint.

Keep docs split by purpose:

- `architecture/` for current and historical architecture references.
- `decisions/` for ADRs.
- `runbooks/` for executable operational procedures.
- `incidents/` for regressions, postmortems, and hidden constraints.
- `tasks/active/` for temporary handoff notes.
- `plans/` for historical plans that must not override current architecture.
- `research/` for external research and source analysis.
- `handoffs/` for historical handoffs and downstream context.
- `reports/` for audits and one-time analysis.

Do not place process rules only in handoffs. Durable rules belong in
`AGENTS.md`, `docs/decisions/`, or `docs/runbooks/`.

Generated outputs do not belong in `docs/`.
