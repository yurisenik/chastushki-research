# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Russian **частушки** (chastushki) generator MVP — scenario input → batch of 4-line rhymed folk verses → quick refinements → history/favorites/export. Product research and design docs live in `docs/`; the bootstrap implementation skeleton (backend + frontend + CI) lives in `backend/`, `frontend/`, `infra/`, `.github/`. The text-generation core exists but persistence, real moderation, form-scoring, and audio are not yet built (see `docs/08_implementation_plan.md`).

## Commands

Backend (run from `backend/`, uses a venv — `make install` creates `.venv` and installs `-e ".[dev]"`):

```bash
make install          # python3 -m venv .venv && pip install -e ".[dev]"
make run              # uvicorn app.main:app --reload --port 8000
make test             # pytest -q
make lint             # ruff check app tests
.venv/bin/pytest tests/test_llm.py::test_llm_error_on_invalid_json -q   # single test
```

Frontend (run from `frontend/`):

```bash
npm install
npm run dev           # next dev (port 3000)
npm run build
npm run lint          # eslint
npm run test          # vitest run
npx vitest run src/components/mvp-form.test.tsx   # single test
```

Both services via Docker: `docker compose up` (root; reads `.env`). CI (`.github/workflows/ci.yml`) runs `pytest -q` (Py 3.13) on backend and `npm run lint && npm run test` on frontend.

## Frontend caveat — read before editing

`frontend/AGENTS.md` (referenced by `frontend/CLAUDE.md`) warns: **this is Next.js 16 with breaking changes** — APIs, conventions, and file structure may differ from training data. Before writing frontend code, read the relevant guide under `frontend/node_modules/next/dist/docs/`. Heed deprecation notices. Default imports use the `@/` alias → `src/` (configured in `tsconfig.json` and `vitest.config.ts`).

## Architecture

### Backend (FastAPI)
- `app/main.py` — app factory + CORS (frontend origins `localhost:3000` / `127.0.0.1:3000`) + router mount.
- `app/api/routes.py` — the **7 endpoints**. The `Pack`-returning endpoints (`/v1/generate-pack`, `/v1/refine`, `/v1/favorites`) save to the store. The store is injected via `Depends(get_store)` (like `get_llm`, overridable in tests). `/v1/refine` rebuilds a `GeneratePackRequest` from the stored source pack and applies a `REFINE_SUFFIX` to the prompt. `/v1/export/{pack_id}` supports `?format=text|json`. `/v1/metrics` derives a `usable_output_rate`. LLM is injected via `Depends(get_llm)` so tests can override it.
- `app/schemas.py` — Pydantic models. `Pack.new(...)` mints `uuid4` + UTC ISO timestamp. `GeneratePackRequest` validates `boldness` 0–5, `count` 3–20. **The API contract (paths + these schema fields) is treated as stable** — extend, don't break, unless a Decision Record in `docs/08_implementation_plan.md` records it. This protects the frontend and `tests/test_api_contracts.py`.
- `app/services/llm.py` — the generation core. `ChastushkaLLM` is the ABC; `_TwoPassLLM` implements two-pass generation (plan → lines) once, delegating a single `_complete()` to each provider:
  - `ClaudeChastushkaLLM` (Anthropic; system prompt sent as a cached block via `cache_control`).
  - `OpenAIChastushkaLLM` (Chat Completions; system prompt as a plain message).
  - `get_llm()` is `@lru_cache`'d and FastAPI dependency; selects provider from `LLM_PROVIDER` env (`openai` default, or `anthropic`/`claude`). Clients are created lazily so importing the module needs no API key. All SDK/network failures are wrapped in `LLMError`, which routes map to HTTP 502.
- `app/prompts.py` — system prompt is **deliberately constant** (no variable interpolation) to enable prompt caching; per-request data goes only in the user message. `build_plan_prompt` / `build_lines_prompt` construct the two user messages.
- `app/services/pipeline.py` — `generate_pack()` runs the LLM, truncates to `request.count`, builds `Candidate`s with form-scoring (`app/services/form.py`, increment 2) and ranks them; applies safe-mode moderation (`app/services/moderation.py`, increment 3). `REFINE_SUFFIX` maps refine actions to prompt suffixes. (The store no longer lives here — see `store.py`.)
- `app/services/store.py` — `PackStore` ABC + `InMemoryPackStore` (default, no DB) + `get_store()` (`@lru_cache`'d FastAPI dependency). `get_store()` returns a `PostgresPackStore` (see `app/services/db_store.py`) when `DATABASE_URL` is set, else `InMemoryPackStore`. Clear with `get_store.cache_clear()` if you change `DATABASE_URL` mid-process.
- `app/db/` — SQLAlchemy 2.0 layer (increment 4). `session.py` exposes `Base` plus lazy module attrs `engine` / `SessionLocal` (PEP 562 `__getattr__`, built from `DATABASE_URL` on first access) and `get_db()`. `models.py` defines `packs` / `candidates` / `favorites`. Migrations live in `backend/alembic/` (`alembic upgrade head`, also `make migrate`); docker-compose runs migrations before uvicorn. `PostgresPackStore` derives `/v1/metrics` from the tables rather than counters.

### Frontend (Next.js 16 / React 19)
- `src/app/` — App Router entry (`page.tsx`, `layout.tsx`).
- `src/components/mvp-workspace.tsx` — client component holding pack/history/favorites state; calls the API. `mvp-form.tsx` is the scenario input form. `tone`/`boldness`/`count` are currently hard-coded in the form (loosening is a later increment).
- `src/lib/api.ts` — thin fetch wrappers against `NEXT_PUBLIC_BACKEND_URL` (default `http://localhost:8000`); types mirror `backend/app/schemas.py` and must stay in sync.
- Tests use Vitest + jsdom + Testing Library (`*.test.tsx`).

### Tests
- Backend contract tests (`tests/test_api_contracts.py`) hit the real FastAPI app via `TestClient`, with the LLM replaced by `StubLLM` and the store forced to a single in-memory instance via `app.dependency_overrides[get_llm]` / `[get_store]` — see the autouse `stub_llm` fixture in `tests/conftest.py`. **No network, `ANTHROPIC_API_KEY`, or DB needed for the contract suite**, even when `DATABASE_URL` is set (as in CI). `tests/test_db_store.py` exercises `PostgresPackStore` against a real Postgres and **skips when `DATABASE_URL` is unset** (CI's postgres service makes it run there). `tests/test_llm.py` tests the two-pass logic against fake Claude/OpenAI clients.
- Frontend tests mirror this: component tests under `src/**/*.test.tsx`.

## Configuration / env

`.env` (gitignored) — copy from `.env.example`. Key vars: `LLM_PROVIDER` (`openai` default | `anthropic`), `OPENAI_API_KEY`/`OPENAI_MODEL`, `ANTHROPIC_API_KEY`, `NEXT_PUBLIC_BACKEND_URL`, `BACKEND_PORT`, `FRONTEND_PORT`, `DATABASE_URL` (empty → in-memory store; docker-compose sets it from `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`). Note `get_llm` and `get_store` are cached; if you change `LLM_PROVIDER` or `DATABASE_URL` mid-process, clear them (`get_llm.cache_clear()` / `get_store.cache_clear()`).

## Working on increments (see `docs/07_execution_playbook.md` + `docs/08_implementation_plan.md`)

The project follows a TDD-first, subagent-decomposed execution mode. For each increment: Red (write/fail a test) → Green (minimal implementation) → Refactor, then verify backend `pytest -q` + `ruff check app tests` and frontend `npm run test` + `npm run lint`. End with a `Changes made` block (what changed, why, where, checks run + result). Increments 1–6 in `08_implementation_plan.md` track the path from the current skeleton to full MVP (LLM gen → form-scoring → moderation → persistence → input form → audio). `docs/README.md` has the recommended reading order for the design/PRD docs.