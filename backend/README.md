# Chastushki Backend

FastAPI backend for MVP generation, refinement, and history endpoints.

## Setup venv (recommended)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## Test and lint

```bash
source .venv/bin/activate
pytest -q
ruff check app tests
```

## Optional Makefile shortcuts

```bash
cd backend
make install
make run
make test
make lint
```
