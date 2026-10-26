PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
COV_MIN ?= 0

.PHONY: test coverage lint format typecheck check

test:
	$(PYTHON) -m pytest -q

coverage:
	$(PYTHON) -m pytest -q --cov --cov-report=term-missing:skip-covered --cov-fail-under=$(COV_MIN)

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

typecheck:  ## lenient, informational (not part of `check`)
	$(PYTHON) -m mypy positionfinder api fretboard

check: lint
	$(PYTHON) manage.py check
	$(PYTHON) manage.py makemigrations --check --dry-run
	$(MAKE) coverage COV_MIN=$(COV_MIN)
