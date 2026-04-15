# Local Runbook

## Start all services

```bash
docker compose up
```

Если backend уже был запущен до обновлений, перезапустите его:

```bash
docker compose down
docker compose up
```

## Backend only

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Backend настроен для CORS с frontend origin:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## Frontend only

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```
