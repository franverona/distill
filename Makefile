.PHONY: dev lint lint-fix format test test-watch

dev:
	uv run fastapi dev app/main.py

lint:
	uv run ruff check app/

lint-fix:
	uv run ruff check --fix app/

format:
	uv run ruff format app/

test:
	uv run pytest tests/ -v

test-watch:
	uv run watchfiles "pytest tests/ -v" app/ tests/