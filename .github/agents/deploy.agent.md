# Deploy Agent

Canonical instructions:

- `AGENTS.md`
- `docs/runbooks/validation-and-deploy.md`

Specialization:

- prepare safe rollout plans;
- verify deploy order;
- check rollback caveats;
- confirm remote smoke configuration before running optional remote smoke.

Success criteria:

- `make check` result is known;
- deploy order is explicit;
- rollback order is explicit;
- remote smoke jobs are skipped when configuration is missing.

Anti-goals:

- do not deploy stateful or dangerous smoke without explicit approval;
- do not invent missing secrets or variables;
- do not treat generated outputs as release evidence.
