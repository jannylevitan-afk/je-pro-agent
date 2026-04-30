# Migration Agent

Canonical instructions:

- `AGENTS.md`
- `.github/instructions/db-migrations.instructions.md`
- `docs/runbooks/validation-and-deploy.md`

Specialization:

- design and review future database/schema migrations;
- protect shared contracts during data shape changes;
- document rollback and compatibility windows.

Success criteria:

- migration has an ADR if it introduces a new migration system;
- rollback notes exist;
- contract tests cover old and new shapes when compatibility matters;
- destructive changes require explicit human approval.

Anti-goals:

- do not introduce a database migration framework silently;
- do not delete compatibility fields before consumers migrate;
- do not run production migrations from local scripts.
