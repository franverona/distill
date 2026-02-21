# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (add --dev for dev tools: ruff, pre-commit, commitizen)
uv sync --dev

# Development server (auto-reload)
make dev

# Linting
make lint          # check for issues
make lint-fix      # check and auto-fix
make format        # format code
```

## Environment

Copy `.env.example` to `.env` before running. The three variables are:
- `DATABASE_URL` — SQLite file path (default: `sqlite:///./distill.db`)
- `OLLAMA_BASE_URL` — local Ollama server (default: `http://localhost:11434`)
- `OLLAMA_MODEL` — model name (default: `llama3.2`)

Ollama must be running (`ollama serve`) and the model pulled (`ollama pull llama3.2`) before requests can be processed.

## Architecture

Layered: **routes → services → repositories → DB**. Services also make outbound HTTP calls (scraper to the target URL, ollama to the local LLM server).

```
app/
├── main.py           # App instance; register the router here
├── config.py         # pydantic-settings Settings class; instantiate as `settings`
├── database.py       # Engine, SessionLocal, Base, get_db() dependency
├── models/           # SQLAlchemy ORM models (inherit from Base)
├── schemas/          # Pydantic v2 schemas for request/response validation
├── routes/           # FastAPI routers; inject DB session via Depends(get_db)
├── services/         # Business logic: scraper.fetch_text(), ollama.summarize()
└── repositories/     # All DB queries; accept a Session as first argument
```

The three endpoints all live in `app/routes/summarize.py` under the prefix `/summarize`:
- `POST /summarize` — scrape → summarize → persist → return
- `GET /summarize/history` — paginated list (`page`, `size` query params)
- `GET /summarize/history/{id}` — single record or 404

## Tooling

- **Ruff** — linter and formatter; config in `[tool.ruff]` in `pyproject.toml`
- **pre-commit** — runs Ruff on `pre-commit` stage and commitizen on `commit-msg` stage
- **commitizen** — enforces Conventional Commits format (`feat:`, `fix:`, `chore:`, etc.)
- **GitHub Actions** — CI runs `lint` and `format --check` on every PR and push to `main`

## Key Conventions

- `get_db()` in `database.py` is a generator dependency; always inject it with `Depends(get_db)` in routes — never instantiate `SessionLocal` directly in a route.
- `pydantic-settings` is a **separate package** from `pydantic`; `Settings` inherits from `BaseSettings`, not `BaseModel`.
- SQLite requires `connect_args={"check_same_thread": False}` on the engine.
- This is a **learning project** — the user fills in `TODO` stubs themselves. Do not implement logic unless explicitly asked.
