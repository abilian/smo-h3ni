## Default target is to run tests
all: test lint


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


## Generate Software Bill of Materials (SBOM) for CRA compliance
generate-sbom:
	@echo "--> Generating SBOM"
	uv sync -q --no-dev
	uv pip list --format=freeze > compliance/requirements-prod.txt
	uv sync -q
	# CycloneDX
	uv run cyclonedx-py requirements \
			--pyproject pyproject.toml -o compliance/sbom-cyclonedx.json \
			compliance/requirements-prod.txt
	# Add license information
	uv run lbom \
			--input_file compliance/sbom-cyclonedx.json \
			> compliance/sbom-lbom.json
	mv compliance/sbom-lbom.json compliance/sbom-cyclonedx.json
	# broken
	#       # SPDX
	#       sbom4python -r compliance/requirements-prod.txt \
	#               --sbom spdx --format json \
	#               -o compliance/sbom-spdx.json
