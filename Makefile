.PHONY: check test typecheck smoke build all

check:
	bash scripts/check.sh

test:
	PYTHONPATH=src:. python3 -m pytest -q

typecheck:
	python3 -m mypy src

smoke:
	CONTENT_ENGINE_SMOKE_MODE=readonly CONTENT_ENGINE_SMOKE_USER_ID=local-smoke-agent PYTHONPATH=src:. python3 scripts/smoke/smoke_readonly_contracts.py --flow contracts

build:
	python3 -m compileall -q src tests

all: check
