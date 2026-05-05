# Season Workspaces

Season workspaces are the durable bridge between the Producer Agent and the rest
of the content factory.

## Purpose

When a person starts a new season, they provide a voice/context seed. Producer
turns that seed into two durable files:

- `producer-output.md`: the human-facing season program shown in the site/admin experience.
- `research-directives.md`: the machine-facing search contract used by Research Agent.

This keeps the approved Producer plan separate from generated run outputs.

## Current Seasons

| Season | Status | Human Output | Search Directives |
|---|---|---|---|
| `2026-04-jane-health-villa` | active current seed | `2026-04-jane-health-villa/producer-output.md` | `2026-04-jane-health-villa/research-directives.md` |

## Agent Reading Rule

For Workflow A hook research in an active season:

1. Read the season `README.md`.
2. Read `research-directives.md`.
3. Use `producer-output.md` only for human-facing context and narrative nuance.
4. Do not use `outputs/` as source of truth.

## Start New Season Pattern

Create a new folder:

```text
docs/seasons/YYYY-MM-season-slug/
├── README.md
├── producer-output.md
└── research-directives.md
```

The new season can reuse the same ProducerOutput display contract, but its
research directives must be generated from that season's actual Producer brief.

