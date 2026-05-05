# Season Workspace Rules

This directory contains durable season workspaces.

Each active season must keep these files:

- `README.md`: season index, status, and file roles.
- `producer-output.md`: canonical human-facing ProducerOutput for the site/admin view.
- `research-directives.md`: canonical machine-facing instructions for Search Agent.

Rules:

- Search Agent reads `research-directives.md`, not generated files in `outputs/`.
- Human review and future admin UI read `producer-output.md`.
- Generated outputs, live scans, and scratch files may reference a season, but they do not replace the workspace.
- A new "Start New Season" action creates a new sibling folder with the same file roles.
- Do not merge multiple seasons into one file.
- If a season changes, update both the human-facing ProducerOutput and the Research Directives when the change affects search.

