.PHONY: test typecheck all

test:
	python3 -m pytest -q

typecheck:
	python3 -m mypy src/ --no-error-summary

all: test typecheck
