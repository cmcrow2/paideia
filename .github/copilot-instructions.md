# Copilot / AI agent instructions — quick orientation

This file gives focused, immediately actionable guidance so an AI coding assistant can be productive in this repository.

## Big picture

- Backend: Python FastAPI service(s) under `backend/` or `app/` (look for `uvicorn` entrypoints in `pyproject.toml` / `backend/main.py`).
- Frontend: Next.js app in `web/` or `frontend/` (inspect `package.json` scripts).
- Vector & ML infra: Pinecone used for vector storage; embedding calls via OpenAI or a local embedding provider. Look for `PINECONE_*` and `OPENAI_*` env vars in `.env.example` or `config/`.
- Orchestration: Docker + `docker-compose.yml` used for local integration tests; CI workflows under `.github/workflows/`.

## How to run locally (developer workflows)

- Python deps (Poetry):
  - `poetry install` (creates venv). If `virtualenvs.in-project` is set, venv is `.venv/`.
- Start backend (dev):
  - `poetry run uvicorn backend.main:app --reload --port 8000`
  - If code uses `app.main:app` or `server:app`, prefer that import — check `pyproject.toml` / `backend/__init__.py`.
- Start frontend:
  - `cd frontend` or `cd web` → `npm install` → `npm run dev` (or `pnpm/yarn` depending on lockfile).
- Tests:
  - `poetry run pytest` (check `tests/`, `conftest.py` for fixtures).
  - For async tests: `pytest-asyncio` may be required; run `poetry run pytest -k <testname>` to run a target.

## Important environment variables & secrets

- `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENV` — used directly in ingestion and query scripts.
- `MATHPIX_APP_ID`, `MATHPIX_APP_KEY` (math OCR) — if project ingests math images.
- Check `.env.example` or `config/` for exact names. Never hardcode keys in PRs.

## Project-specific conventions & patterns

- **Vector ingestion pattern**: text chunks are prepared with metadata `{page, source, chunk_type}` and uploaded in batches to Pinecone — look for `upsert`, `index.create`, or `pinecone.Index(...).upsert(...)` usage. Preserve `page` metadata for provenance.
- **Math OCR**: Math content may use Mathpix for LaTeX; prefer storing both raw LaTeX and a short human-readable description (for embeddings).
- **Chunking**: Chunks aim to keep equations and surrounding paragraphs together (custom `TextSplitter` may be implemented).
- **Streaming**: Backend uses streaming endpoints for token-by-token responses (look for `ReadableStream`, `StreamingStdOutCallbackHandler`, `langgraph` or `streaming` handlers).
- **Hybrid retrieval**: Some retrieval flows combine sparse (keyword) and dense (embedding) retrieval; search for `BM25`, `FAISS`, or `sparse` modules.

## Where to look (key files & directories)

- `pyproject.toml` — dependencies and scripts (Poetry).
- `app/` — FastAPI endpoints and ingestion scripts.
- `scripts/` — helpful dev scripts (index creation, migration, ingestion).
- `tests/`, `conftest.py` — test patterns and fixtures, including any pytest-asyncio usage.

## When making changes

- Keep provenance & metadata when touching ingestion code (do not remove `page`/`source` fields).
- Respect batch size and rate-limit logic for external APIs (OpenAI / Mathpix / Pinecone); keep exponential backoff / retry semantics when present.
- When modifying retrieval prompts or chunking, add unit/integration tests demonstrating improved retrieval for a small set of representative queries.

## Goals of this file

- Provide enough repository-specific context for an AI to: run tests, locate relevant code to change, and produce safe, provable edits that preserve metadata and integration behavior.
- Do not assume hidden infra or undocumented secrets — surface any missing `README` gaps as TODOs in PR descriptions.
