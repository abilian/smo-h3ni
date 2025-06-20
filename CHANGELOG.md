# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog documents the changes made by Abilian as part of the H3NI project's fork of the original SMO.

## [Unreleased]

### Added

- **Command Line Interface:** Implemented a basic CLI to interact with the SMO API.

### Fixed

- **WSGI Application Path:** Corrected the import path for the WSGI application to ensure it can be properly located and served.
- **Integration Test Bugs:** Resolved issues in the codebase that were discovered while writing new integration tests.

### Refactored

- **Project Structure:** Reorganized the entire codebase into a top-level `smo` package, improving modularity and namespace clarity.
- **Static Analysis:** Integrated `ruff` for static analysis and linting, and fixed all reported issues to improve code quality and consistency.
- **Code Formatting:** Formatted the entire source tree for improved readability and consistency.
- **Placement Algorithm:** Cleaned up the placement algorithm code and added corresponding tests.
- **General Cleanup:** Performed various small code cleanups, optimizations, and sorted imports across the project.

### Docs

- **Development Roadmap:** Updated the `TODO.md` file to reflect the current development plan and progress.
- **README and Notes:** Updated the `README.md` and added supplementary documentation and notes.

### Tests

- **CI Pipeline:**
    - Set up a Continuous Integration pipeline on SourceHut.
    - Performed numerous fixes to stabilize CI builds on both SourceHut and GitLab.
- **Test Organization:** Grouped and cleaned up test files for better structure and maintainability.
- **Dockerized Tests:** Added a `Dockerfile` for running the test suite in a containerized environment.
- **Integration Testing with In-Memory DB:** Added integration tests for the Flask application using `py-pglite`, an in-memory PostgreSQL engine.
- **Initial Test Suite:** Introduced basic unit tests and configured integration tests to run via `nox`.

### Chore

- **Dependency Management:** Converted the project to use modern Python packaging standards (PEP 621, PEP 517) with a `pyproject.toml` file.
- **Development Tooling:**
    - Tweaked the `Makefile` to streamline common development tasks.
    - Added `devtools` to improve the debugging experience.
- **Dependencies:** Updated project and development dependencies to their latest versions.
- **Compliance Tooling:**
    - Generated a Software Bill of Materials (SBOM) for compliance.
    - Added license files and headers to ensure the project is compliant with the REUSE Specification.
