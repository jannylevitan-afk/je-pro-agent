# ADR 0002: Season Workspace Contract

**Status:** Accepted  
**Date:** 2026-05-05

## Context

Producer creates a human-facing season program from a spoken or written human
seed. That output is not a random generated artifact: it is the approved format
the future site/admin experience should show to the person.

At the same time, Research Agent needs a concise and deterministic search
contract. Using `outputs/` directly as the source of truth creates ambiguity
because generated runs, blocked research boards, and scratch outputs can all live
there.

## Decision

Add durable season workspaces under `docs/seasons/`.

Each season workspace contains:

- `producer-output.md`: the canonical human-facing ProducerOutput for the site/admin view.
- `research-directives.md`: the canonical machine-facing Search Agent contract.
- `README.md`: season status, file roles, and topic targets.

For the current Jane season, the active workspace is:

```text
docs/seasons/2026-04-jane-health-villa/
```

Research Agent must read `research-directives.md` before Workflow A hook research.
Future "Start New Season" flows create a new sibling workspace with the same file
roles.

## Consequences

- Human-facing ProducerOutput is preserved in the approved display format.
- Search Agent no longer depends on generated `outputs/` files.
- Multiple seasons can coexist without mixing research context.
- Topic targets, platform targets, and gate rules become season-specific and auditable.
- The admin/site layer can show the season program while pipeline agents consume
  narrower machine directives.

## Non-Goals

- This does not build the browser UI yet.
- This does not make Producer perform live search.
- This does not turn `outputs/` into source of truth.

