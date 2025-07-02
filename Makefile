## Default target is to run tests
all: test lint


## Help
help:
	@adt help-make


## Default target to run tests
test:
	make test-wo-db
	make test-w-db

test-wo-db:
	uv run pytest tests/a_unit tests/b_integration


test-w-db:
	@echo "⏳ Starting Postgres with Docker Compose..."
	COMPOSE_PROJECT_NAME=smo-tests docker compose -f docker-compose.test.yml up -d --wait
	@echo "✅ Running pytest on $(TEST_PATH)..."
	uv run pytest tests/c_e2e
	@echo "🧹 Tearing down Docker Compose..."
	COMPOSE_PROJECT_NAME=smo-tests docker compose -f docker-compose.test.yml down


## Test with Beartype
test-beartype:
	uv run pytest --beartype-packages=smo


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

## Format
format:
	uv run isort src tests
	uv run black src tests
	uv run ruff format src tests

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


## Generate Software Bill of Materials (SBOM) from venv for CRA compliance
generate-sbom:
	@echo "--> Generating SBOM (assuming syft is installed)"
	make clean
	uv sync -q --no-dev
	uv pip list --format=freeze > compliance/requirements-prod.txt
	syft .venv \
		-o spdx-json=compliance/sbom-spdx.json \
		-o cyclonedx-json=compliance/sbom-cyclonedx.json \
		-o syft-text=compliance/sbom-syft.txt
	npx prettier -w compliance/sbom-spdx.json
	npx prettier -w compliance/sbom-cyclonedx.json
	uv sync -q
