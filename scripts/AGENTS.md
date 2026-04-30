# Scripts Rules

Scripts must be small, readable, and safe by default.

Smoke scripts must live in `scripts/smoke/` and follow `scripts/smoke/README.md`.

No script may require live mutation unless its filename and README section mark it
as stateful/dangerous.

Use explicit environment variables. Do not read secrets from hardcoded paths.

Repo-wide validation lives in `scripts/check.sh` and must stay readable enough for
an agent to audit in under one minute.
