## Default target is to run tests
all: test


## Help
help:
	@adt help-make


## Default target to run tests
test:
	uv run pytest


## Alias for checking code quality
lint: check

## Lint the codebase using Ruff and possibly other tools
check:
	uv run ruff check src


## Setup the development environment
develop:
	uv sync


## Update dependencies and check for outdated packages
update:
	uv sync -U
	uv pip list --outdated


## Clean build artifacts
clean:
	uv run adt clean


## Format documentation files
format-doc:
	uv run markdown-toc -i README.md
	uv run markdown-toc -i TODO.md

# Extra targets for manual git synchronization (will be run by CI later)

## Sync code with remote repositories
sync-code:
	git pull eclipse h3ni
	git pull gh h3ni
	git pull sourcehut h3ni
	@make push-code


## Push code to remote repositories
push-code:
	git push eclipse h3ni
	git push gh h3ni
	git push sourcehut h3ni
