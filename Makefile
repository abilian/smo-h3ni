all: test

test:
	uv run pytest


check:
	uv run ruff check src


develop:
	uv sync

update:
	uv sync -U
	uv pip list --outdated
