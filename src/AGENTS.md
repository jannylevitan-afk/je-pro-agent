# Source Code Rules

Shared contracts live in `src/content_engine/models/`.

Pure business behavior lives in `src/content_engine/services/`.

Orchestration lives in `src/content_engine/orchestration/`.

Runtime entrypoints live in `src/content_engine/runtime/`.

Before changing `orchestration/live_pipeline.py`, prefer adding or proving behavior
in a pure service and test first.

Do not add network calls to services that are intended to be deterministic.
Research Agent remains the only layer that collects external data.

Validation for source changes:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/relevant_test.py
make check
```
