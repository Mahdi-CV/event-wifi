.PHONY: install test lint inventory

install:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e '.[dev]'

test:
	.venv/bin/python -m pytest

inventory:
	./scripts/inventory-adapters.sh
