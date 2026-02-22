# Testing Plan

This document outlines how to add tests to the Distill project, from setting up
the environment to writing each test file. Only the critical parts are covered:
the repository layer, the two services, and the route handlers.

---

## 1. Dependencies

Add to the `dev` dependency group in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    ...
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",  # needed for async test functions
]
```

Then sync:

```bash
uv sync --dev
```

`httpx` is already a project dependency, so no extra install is needed —
FastAPI's test client is built on top of it.

`watchfiles` is also already installed as part of `fastapi[standard]`, so the
test watcher command requires no extra dependency either.

---

## 2. pytest configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # makes every async test function run automatically, no decorator needed
```

---

## 3. Makefile

Add `test` and `test-watch` targets immediately so you can run tests as soon as
the first one exists:

```makefile
.PHONY: dev lint lint-fix format test test-watch

test:
	uv run pytest tests/ -v

test-watch:
	uv run watchfiles "pytest tests/ -v" app/ tests/
```

- `make test` — runs the full test suite once
- `make test-watch` — re-runs tests automatically whenever a file in `app/` or
  `tests/` changes; no need to manually re-run after every edit

---

## 4. Folder structure

Mirror the `app/` layout so each source file has a clearly corresponding test
file:

```
tests/
├── __init__.py
├── conftest.py                    # shared fixtures used across all test files
├── repositories/
│   ├── __init__.py
│   └── test_summary.py            # tests for app/repositories/summary.py
├── services/
│   ├── __init__.py
│   ├── test_scraper.py            # tests for app/services/scraper.py
│   └── test_ollama.py             # tests for app/services/ollama.py
└── routes/
    ├── __init__.py
    └── test_summarize.py          # tests for app/routes/summarize.py
```

---

## 5. conftest.py — shared fixtures

This is the most important file. It sets up:

- An **in-memory SQLite database** used only during tests (never touches `distill.db`)
- A **database session** that each test receives and that is rolled back after each test
- A **FastAPI test client** that uses the test database instead of the real one

### How dependency override works

FastAPI allows replacing any `Depends(...)` dependency at test time via
`app.dependency_overrides`. You use this to swap `get_db` (which opens the real
DB) with a function that returns the test session instead.

### Steps to implement `conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# TODO: Create an in-memory SQLite engine for tests
#   Hint: use "sqlite:///:memory:" as the URL
#   Hint: still needs connect_args={"check_same_thread": False}

# TODO: Create a TestingSessionLocal factory bound to the test engine

# TODO: Create all tables in the in-memory DB before tests run
#   Hint: Base.metadata.create_all(bind=test_engine)

# TODO: Define a `db_session` pytest fixture (scope="function") that:
#   1. Opens a TestingSessionLocal session
#   2. Yields it to the test
#   3. Closes it after the test

# TODO: Define a `client` pytest fixture that:
#   1. Overrides app.dependency_overrides[get_db] with a function
#      that yields the db_session fixture
#   2. Creates a TestClient(app) and yields it
#   3. Clears app.dependency_overrides after the test
#
#   Example structure:
#     def override_get_db():
#         yield session  # the session from db_session fixture
#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as client:
#         yield client
```

---

## 6. tests/repositories/test_summary.py — unit tests

These tests exercise the repository functions directly against the in-memory DB.
No HTTP calls are involved.

Each test receives the `db_session` fixture from `conftest.py`.

### Tests to implement

#### `create`
```python
# TODO: Call summary_repo.create(db, url=..., summary=..., model=...)
# TODO: Assert the returned record has the correct url, summary, model
# TODO: Assert id is not None (DB assigned it)
# TODO: Assert created_at is not None (DB set it automatically)
```

#### `get_by_id` — found
```python
# TODO: Insert a record using summary_repo.create(...)
# TODO: Call summary_repo.get_by_id(db, record.id)
# TODO: Assert the returned record matches what was inserted
```

#### `get_by_id` — not found
```python
# TODO: Call summary_repo.get_by_id(db, 99999)
# TODO: Assert the result is None
```

#### `get_all` — pagination
```python
# TODO: Insert 3 records using summary_repo.create(...) three times
# TODO: Call summary_repo.get_all(db, page=1, size=2)
# TODO: Assert total == 3
# TODO: Assert len(items) == 2
# TODO: Assert page == 1 and size == 2
```

#### `get_all` — empty
```python
# TODO: Call summary_repo.get_all(db) without inserting anything
# TODO: Assert total == 0 and items == []
```

---

## 7. tests/services/test_scraper.py — unit tests

`fetch_text` makes a real HTTP request, so tests must mock the network.
Use `unittest.mock.patch` to replace `httpx.AsyncClient.get` with a fake response.

### How to mock httpx

```python
from unittest.mock import AsyncMock, MagicMock, patch

mock_response = MagicMock()
mock_response.text = "<html>...</html>"
mock_response.raise_for_status = MagicMock()  # does nothing (no error)

with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
    result = await fetch_text("https://example.com")
```

### Tests to implement

#### Returns plain text from HTML
```python
# TODO: Mock the HTTP response with simple HTML:
#   "<html><body><p>Hello world</p></body></html>"
# TODO: Call fetch_text("https://example.com")
# TODO: Assert "Hello world" is in the result
```

#### Strips script and style tags
```python
# TODO: Mock the HTTP response with HTML containing <script> and <style> tags:
#   "<html><head><style>body{}</style></head>
#    <body><script>alert(1)</script><p>Real content</p></body></html>"
# TODO: Call fetch_text(...)
# TODO: Assert "Real content" is in the result
# TODO: Assert "alert" is NOT in the result
# TODO: Assert "body{}" is NOT in the result
```

#### Raises on HTTP error
```python
# TODO: Mock raise_for_status() to raise httpx.HTTPStatusError
# TODO: Assert that fetch_text(...) raises httpx.HTTPStatusError
#   Hint: use pytest.raises(httpx.HTTPStatusError)
```

---

## 8. tests/services/test_ollama.py — unit tests

`summarize` posts to the Ollama API. Mock `httpx.AsyncClient.post` to avoid
needing a real Ollama server during tests.

### Tests to implement

#### Returns the summary from the response
```python
# TODO: Mock the HTTP POST response to return:
#   {"response": "This is the summary."}
# TODO: Call ollama.summarize("some long article text")
# TODO: Assert the result == "This is the summary."
```

#### Sends the correct payload to Ollama
```python
# TODO: Mock AsyncClient.post and capture what it was called with
#   Hint: AsyncMock records calls — check mock.call_args
# TODO: Call ollama.summarize("article text")
# TODO: Assert the JSON body contains the correct model (settings.ollama_model)
# TODO: Assert stream is False in the payload
# TODO: Assert the prompt contains the input text
```

#### Raises on Ollama error
```python
# TODO: Mock raise_for_status() to raise httpx.HTTPStatusError
# TODO: Assert that summarize(...) raises httpx.HTTPStatusError
```

---

## 9. tests/routes/test_summarize.py — integration tests

These tests send real HTTP requests to the app using the `TestClient` from
`conftest.py`, but with the real DB replaced by the in-memory one and the
external services (scraper, ollama) mocked out.

Each test receives the `client` fixture from `conftest.py`.

### Tests to implement

#### `POST /summarize` — success (201)
```python
# TODO: Mock scraper.fetch_text to return "article text" (AsyncMock)
# TODO: Mock ollama.summarize to return "the summary" (AsyncMock)
# TODO: POST to "/summarize" with body {"url": "https://example.com"}
# TODO: Assert status code == 201
# TODO: Assert response JSON contains url, summary, model, id, created_at
```

#### `POST /summarize` — invalid URL (422)
```python
# TODO: POST to "/summarize" with body {"url": "not-a-url"}
# TODO: Assert status code == 422 (Pydantic validation error)
```

#### `GET /summarize/history` — returns list
```python
# TODO: Insert a record directly via summary_repo.create(...) using db_session
# TODO: GET "/summarize/history"
# TODO: Assert status code == 200
# TODO: Assert response JSON contains "items", "total", "page", "size"
# TODO: Assert total == 1
```

#### `GET /summarize/history/{id}` — found (200)
```python
# TODO: Insert a record via summary_repo.create(...)
# TODO: GET f"/summarize/history/{record.id}"
# TODO: Assert status code == 200
# TODO: Assert response JSON id matches the inserted record
```

#### `GET /summarize/history/{id}` — not found (404)
```python
# TODO: GET "/summarize/history/99999"
# TODO: Assert status code == 404
# TODO: Assert response JSON detail == "Not found"
```

---

## 10. CI

Add a test step to the existing `lint` job in `.github/workflows/ci.yml`, after
the formatter step:

```yaml
      - name: Run tests
        run: make test
```
