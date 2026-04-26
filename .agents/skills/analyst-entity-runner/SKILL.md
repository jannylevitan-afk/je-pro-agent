---
name: analyst-entity-runner
description: Use when running the Analyst Entity from Codex CLI or a local terminal for Workflow B handoff, SourceItem analysis, Writer Entity TZ generation, or Admin Operating Hub-ready Analyst reports.
---

# Analyst Entity Runner

## Overview

Run the Analyst Entity after the Research Agent has produced valid `SourceItem` JSON. The entity performs Workflow B Phase 1 and Phase 2, then emits Source Notes, Insight Cards, and Writer Entity TZ handoffs for the Admin Operating Hub.

## Command

Use module mode inside the repo, or the installed console script:

```bash
PYTHONPATH=src python3 -m content_engine.cli.analyst \
  --input examples/analyst_source_items.sample.json \
  --output outputs/analyst_entity_report.md \
  --json-output outputs/analyst_entity_report.json
```

```bash
content-engine-analyst \
  --input examples/analyst_source_items.sample.json \
  --output outputs/analyst_entity_report.md \
  --json-output outputs/analyst_entity_report.json
```

## Input Contract

Accepted JSON shapes:

- A raw list of `SourceItem` objects.
- An object with `source_items: [...]` and optional `verified_facts: [...]`.

Required environment:

- `ANTHROPIC_API_KEY`

Optional environment:

- `ANTHROPIC_MODEL`
- `ANTHROPIC_API_BASE`
- `ANTHROPIC_VERSION`
- `CONTENT_ENGINE_REQUEST_TIMEOUT_SECONDS`

## Output Contract

- Markdown report for human review.
- JSON report with `entity: analyst`, `destination: admin_operating_hub`, and `notion_enabled: false`.
- Each report must include source note, insight card, preflight status, risk flags, and per-lane `writer_tz`.

## Guardrails

- Do not write to Notion.
- Do not invent missing facts; pass only source-backed insights and verified facts.
- If preflight flags are present, keep the report but treat it as review-required before Writer Entity execution.
