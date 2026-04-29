# Tests Rules

Prefer targeted tests first:

```bash
PYTHONPATH=src:. pytest -q tests/path/to/test_file.py
```

Then run full validation:

```bash
PYTHONPATH=src:. pytest -q
python3 -m mypy src
```

New contracts need `tests/models/`.

New deterministic services need `tests/services/`.

New orchestration behavior needs `tests/orchestration/` and should avoid live APIs.
