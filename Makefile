.PHONY: dev lint lint-fix format test test-watch

dev:
	uv run fastapi dev app/main.py

lint:
	uv run ruff check app/ tests/

lint-fix:
	uv run ruff check --fix app/ tests/

format:
	uv run ruff format app/ tests/

test:
	uv run pytest tests/ -v

test-watch:
	uv run watchfiles "pytest tests/ -v" app/ tests/