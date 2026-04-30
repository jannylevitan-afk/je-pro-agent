#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-src:.}"

python3 -m compileall -q src tests

CONTENT_ENGINE_SMOKE_MODE="${CONTENT_ENGINE_SMOKE_MODE:-readonly}" \
CONTENT_ENGINE_SMOKE_USER_ID="${CONTENT_ENGINE_SMOKE_USER_ID:-local-smoke-agent}" \
PYTHONPATH="$PYTHONPATH" \
python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts

python3 -m pytest -q
python3 -m mypy src
