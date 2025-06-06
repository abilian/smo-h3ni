all: test

test:
	uv run pytest


lint: check

check:
	uv run ruff check src


develop:
	uv sync


update:
	uv sync -U
	uv pip list --outdated


clean:
	uv run adt clean


format-doc:
	uv run markdown-toc -i README.md
	uv run markdown-toc -i TODO.md
