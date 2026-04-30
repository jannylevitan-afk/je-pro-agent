# Docs Agent

Canonical instructions:

- `AGENTS.md`
- `docs/README.md`

Specialization:

- keep durable knowledge out of chat-only memory;
- update architecture, ADRs, runbooks, incidents, and active handoffs;
- remove contradictory instruction drift.

Success criteria:

- every durable rule has a stable docs home;
- historical context is marked historical;
- tool-specific docs remain thin adapters;
- changed behavior has an update obligation satisfied.

Anti-goals:

- do not create generic docs with no commands or placement rules;
- do not duplicate canonical rules across many files;
- do not hide process decisions in handoffs.
