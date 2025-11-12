# paideia

An AI assistant that ingests college-level math textbooks (PDFs), creates embeddings and searchable chunks, and exposes a FastAPI service for question-answering and tutoring workflows.

This repository contains the API and ingestion scaffolding used to:

- convert PDFs into page-aware chunks
- embed chunks using OpenAI embeddings
- upsert vectors to Pinecone
- serve an FAQ/chat retrieval endpoint via FastAPI (streaming responses supported)

Key goals: make math textbook content queryable, preserve page/source metadata, and enable hybrid retrieval for accurate answers.

## Quick architecture summary

- API: FastAPI app at `app/main.py` (FastAPI instance `app.main.app`); health/root endpoint at `/`.
- Ingestion: `pdfs/` is the source folder for PDFs. Ingestion pipeline (OCR/chunking → embeddings → Pinecone upsert) is described in the repository docs and `.github/copilot-instructions.md`.
- Embeddings & store: OpenAI embeddings (configured via env vars) and Pinecone for vector storage.
- Dev: Poetry-managed environment. Python 3.13 is the targeted interpreter (see `pyproject.toml`).

## Getting started (developer)

Prerequisites

- Python 3.13
- Poetry (dependency management)
- Account/API keys for OpenAI and Pinecone (set via environment variables)

Install dependencies

```bash
poetry install --no-root
```

Environment variables

Create a `.env` (or export in your shell) with the required keys. Typical variables used by this project:

- OPENAI_API_KEY - OpenAI API key
- PINECONE_API_KEY - Pinecone API key
- PINECONE_ENV - Pinecone environment/region
- (Optional) MATHPIX or OCR-related keys if OCR is used in ingestion

Run the API locally

```bash
# run with uvicorn via poetry
poetry run uvicorn app.main:app --reload --port 8000
```

A quick sanity check

```bash
curl -s http://127.0.0.1:8000/ | sed -n '1,20p'
```

Run tests and linters

```bash
poetry run pytest -q
```

## Important files & where to look

- `app/main.py` — FastAPI app entrypoint and CORS/health configuration. This is where the server and endpoints are declared.
- `pdfs/` — place source PDFs here for ingestion. Ingestion code (if present) will read from this dir.
- `pyproject.toml` — dependency manifest (FastAPI, uvicorn, OpenAI, Pinecone, LangChain, numpy, sympy, etc.) and dev tools (pytest, black, ruff).
- `.github/copilot-instructions.md` — project-specific guidance for AI agents (ingestion flow, chunk metadata, embedding expectations). See this for pipelines and conventions.

## Project-specific conventions and patterns

- Chunk metadata: chunks are expected to include `source`, `page`, and `chunk_type` metadata so answers can reference original pages. See the ingestion guidance in `.github/copilot-instructions.md`.
- Streaming endpoints: API supports streaming token-by-token responses for long answers. When adding new endpoints, adopt the same streaming pattern used in `app/main.py`.
- Hybrid retrieval: the stack uses dense embeddings (OpenAI) with Pinecone and is designed to support sparse or keyword augmentation when needed. Keep retrieval and reranking logic separate from presentation.

## Development notes

- Target Python: 3.13 (see `pyproject.toml`). Use Poetry to manage the virtualenv and run commands through `poetry run`.
- Formatting: use `black` and `ruff` (configured in dev deps). Run them before creating PRs.
- Tests: `pytest` and `pytest-asyncio` are included. Add small unit tests for ingestion transforms and retriever logic.

## Adding documents

1. Drop PDFs into `pdfs/`.
2. Run the ingestion pipeline (see `.github/copilot-instructions.md` for the exact script and required environment variables). The pipeline will OCR/chunk/embed and upsert vectors into Pinecone.

## How you can help / contribute

- Improve ingestion reliability (OCR edge cases, math-heavy pages).
- Add unit/integration tests for vector ingest and retrieval.
- Add CI (Github Actions) to run linters and tests on PRs.

## License

See `LICENSE` in the repository root.
