PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: venv install run test lint

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -e ".[dev]"

run:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port 8000

test:
	$(VENV_PYTHON) -m pytest -q

lint:
	$(VENV_PYTHON) -m ruff check app tests
