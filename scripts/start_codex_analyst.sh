#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="$ROOT/.codex/agents/analyst_entity.md"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Analyst prompt not found: $PROMPT_FILE" >&2
  exit 1
fi

TASK="${*:-Подними Analyst Entity, прочитай источники правды проекта и жди вход Research Agent для Workflow B Phase 1/2.}"
PROMPT="$(cat "$PROMPT_FILE")

## Current Task

$TASK"

exec codex \
  --cd "$ROOT" \
  --model "${CODEX_ANALYST_MODEL:-gpt-5.4}" \
  --sandbox "${CODEX_ANALYST_SANDBOX:-workspace-write}" \
  --search \
  "$PROMPT"
