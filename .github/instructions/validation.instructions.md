# Validation Instructions

Use targeted validation first, then full validation.

```bash
PYTHONPATH=src:. pytest -q tests/path/to/test_file.py
PYTHONPATH=src:. pytest -q
python3 -m mypy src
```

For smoke changes:

```bash
CONTENT_ENGINE_SMOKE_MODE=readonly \
CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent \
PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py
```

If any command fails, report the exact command and failure. Do not claim completion.
