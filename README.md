# Je Pro Agent

This project is set up as a standalone repository so it stays fully isolated from other work.

## Current Structure

- `docs/architecture/` — reference architecture and source materials
- `docs/notes/` — working notes and briefs
- `docs/superpowers/specs/` — design notes for the setup
- `docs/superpowers/plans/` — implementation planning notes
- `src/` — Content Engine application code
- `knowledge/kmd/` — generated workflow knowledge material for Research Agent handoff
- `examples/seed_config.sample.yaml` — approved blog source pool and discovery rules
- `assets/` — static assets

## Current Reference File

The current architecture document lives at:

- `content_engine_architecture_v3.md`

## Runtime Notes

- Research Agent collects and tags source items; workflows only process prepared inputs.
- Source discovery expands from the approved seed pool in `examples/seed_config.sample.yaml`.
- Workflow A/B can write `.kmd.md` material files through `CONTENT_ENGINE_KMD_ROOT`.
- Workflow A video intake preserves video title, caption/transcript, source refs, and public metrics before scripting.
- Workflow A returns `script_ready` n8n/Telegram payloads after creating Script + Filming Card records.
- Workflow B Analyst Entity can run from CLI and produce Source Notes, Insight Cards, and Writer Entity TZ files:
  `PYTHONPATH=src python3 -m content_engine.cli.analyst --input examples/analyst_source_items.sample.json --output outputs/analyst_entity_report.md --json-output outputs/analyst_entity_report.json`.
- Optional n8n webhook dispatch is enabled with `N8N_WEBHOOK_URL`.
- Admin Operating Hub is the intended output layer; Notion is not required for Analyst CLI runs.
