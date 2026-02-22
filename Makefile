.PHONY: dev lint lint-fix format test test-watch migrate

dev:
	uv run fastapi dev app/main.py

lint:
	uv run ruff check app/ tests/ alembic/

lint-fix:
	uv run ruff check --fix app/ tests/ alembic/

format:
	uv run ruff format app/ tests/ alembic/

test:
	uv run pytest tests/ -v

test-watch:
	uv run watchfiles "pytest tests/ -v" app/ tests/ alembic/

migrate:
	uv run alembic upgrade head