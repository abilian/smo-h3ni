# TODO

Here are the refactorings and enhancements for the SMO codebase planned or envisioned to achieve the H3NI project's goals successfully.

<!-- toc -->

- [Quick changelog and task list](#quick-changelog-and-task-list)
  * [DONE](#done)
  * [Roadmap / Started](#roadmap--started)
  * [Roadmap / TODO](#roadmap--todo)
  * [Roadmap / Long-term](#roadmap--long-term)
- [Detailed discussion](#detailed-discussion)
  * [0. Starting point](#0-starting-point)
  * [1. Foundational Refactorings](#1-foundational-refactorings)
  * [2. New SMO Refactorings/Enhancements Driven Directly by H3NI Functionalities](#2-new-smo-refactoringsenhancements-driven-directly-by-h3ni-functionalities)
  * [Already Done](#already-done)
  * [Summary](#summary)

<!-- tocstop -->

## Quick changelog and task list

Starting point = the orignal repository ([commit 6590688b51b6487da414b4d80598e57594954593](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/smo/-/tree/6590688b51b6487da414b4d80598e57594954593))

### DONE

- [x] Introduce SMO-specific namespace for better organization.
- [x] Add basic unit tests for functionality validation.
- [x] Create a CI pipeline on SourceHut.
- [x] Introduce a `Makefile` to streamline hypermodern Python development workflows (e.g., testing, linting, formatting).
- [x] Refact: Refactor codebase for readability and maintainability.
- [x] Test: Basic integration tests with py-pglite
- [x] Compliance: Add licencing check using REUSE
- [x] Compliance: generate a SBOM
- [x] Implement static analysis (ruff) and enforce consistent formatting.
- [x] DX: Add support for local development with Vagrant.
- [x] Test: Extend test capabilities to include runtime type-checking Beartype.
- [x] Doc: Introduce a Changelog
- [x] Refact: Refactor using a layered architecture.

### Roadmap / Started

- [ ] Feat: Add SQLite support for database flexibility.
- [ ] Doc: Update documentation for usage and contribution guidelines (README)
- [ ] Feat: Implement a basic CLI for interacting with the SMO API.
- [ ] Type: Add type hints to all functions and methods.

### Roadmap / TODO

- [ ] test: Add more unit tests in order to reach close to 100% coverage.
- [ ] test: Add integration tests.
- [ ] test: Add e2e tests.
- [ ] test: test Swagger API using [Schemathesis](https://github.com/schemathesis/schemathesis?tab=readme-ov-file) (and/or [Bravado](https://pypi.org/project/pytest-bravado/)). (But not Dredd - Dredd is dead, killed by Oracle)
- [ ] feature: Improve error handling and logging.
- [ ] refact: use the modern (2.0) SQLAlchemy ORM API.
- [ ] feature: Implement a proper configuration management.
- [ ] feature: Implement a dependency injection mechanism.
- [ ] feature: Implement an extension mechanism (e.g. `pluggy` or similar).
- [ ] doc: Create a proper documentation site using Portray or MkDocs (cf. <https://lab.abilian.com/Tech/Python/Tooling/Documentation/>)
- [ ] doc: Describe python API using a formalized format (cf. <https://lab.abilian.com/Tech/Python/Tooling/Documenting%20a%20Python%20API/>)
- [ ] fix: Work around the `hdarctl` dependency issue.

### Roadmap / Long-term

- [ ] refact: make the optimizer pluggable.
- [ ] feat: make the orchestration backend-end (current, Kubernetes) pluggable.
- [ ] refact: make the orchestrator pluggable.
- [ ] feat: create plugins for other orchestrators: Nomad, Docker Swarm, OpenNebula, Hop3 (when it's ready), etc.
- [ ] feat: Make a Web UI.
- [ ] refact: Make the optimisation algorithm pluggable.
- [ ] feat: Create and benchmark alternative optimisation algorithms.
- ...


## Detailed discussion

### 0. Starting point

See [Codebase Tour](./notes/codebase-tour.md).

### 1. Foundational Refactorings

See [Refactoring Plan](./notes/refactoring-plan.md).

More specifically:

1.  **Decouple Business Logic from Flask:**
    *   **H3NI Relevance:** The plan mentions integrating "potentially directly with its Python API for tighter coupling, if beneficial and maintainable". A clean Python API is only possible if the core SMO logic (services) is independent of Flask specifics.
    *   **SMO Impact:** This is paramount. The `graph_service.py` and other logic must be callable without a Flask app context.

2.  **Externalize Configuration and Constants:**
    *   **H3NI Relevance:** New mechanisms like "Energy-Aware Orchestration" will introduce new parameters (e.g., node energy efficiency, renewable energy source availability). Predictive scaling might have model paths or hyperparameters. These *must not* be hardcoded.
    *   **SMO Impact:** `utils/constant.py` needs to be almost entirely replaced by dynamic configuration loading. SMO needs to understand how to get these new parameters for its placement/scaling decisions.

3.  **Introduce Dependency Injection and/or Plugins:**
    *   **H3NI Relevance:** As SMO becomes a platform for H3NI extensions, being able to inject different implementations (e.g., for ML model predictors, energy data sources) will be key for modularity and testability.
    *   **SMO Impact:** Core services should be designed to receive their dependencies rather than instantiating them directly.

4.  **Eliminate Global State:**
    *   **H3NI Relevance:** For stable Python API usage and robust extensions, global state is problematic. If H3NI extensions run within the SMO process, shared global state can lead to unpredictable interactions.
    *   **SMO Impact:** Critical for creating a stable platform for H3NI extensions.

5.  **Continuous Integration:**
    *   **H3NI Relevance:** The plan explicitly states "Maintain and enhance the CI pipeline...".
    *   **SMO Impact:** The existing CI (from the refactored codebase, e.g., `noxfile.py`) needs to be robust and cover any new functionalities and APIs.
    *   **Testing:** The CI should include unit tests for the new functionalities and integration tests for the H3NI extensions.
    *   **Gitlab CI**: the updated code base should be tested with the Gitlab CI pipeline within the Eclipse infrastructure.
    *   **Sourcehut CI**: for consistency and future maintenance, the updated code base also should be tested with the Sourcehut CI pipeline within the Abilian infrastructure.

6.  **Refine Error Handling and Define Custom Exceptions:**
    *   **H3NI Relevance:** Clear error reporting between Hop3, the Hop3 Plugin, SMO, and H3NI extensions will be crucial. Custom exceptions will help pinpoint where issues arise.
    *   **SMO Impact:** Important for robust integration.


### 2. New SMO Refactorings/Enhancements Driven Directly by H3NI Functionalities

Here's a list of areas where the SMO's current capabilities need to be extended or significantly modified:

1.  **Pluggable and Extensible Placement & Scaling Algorithms:**
    *   **H3NI Relevance:**
        *   "ML-Driven Predictive Scaling": SMO scaling algorithm (`decide_replicas`) needs to incorporate predictive inputs.
        *   "Energy-Aware Orchestration": SMO placement algorithm (`decide_placement`) needs to consider energy factors.
        *   "H3NI Orchestration Mechanisms": These H3NI mechanisms will "Consult" the "SMO Core" for "Resource Allocation, Scaling Decisions." This implies SMO needs to expose an internal API or have its core decision logic be callable/influenceable by these extensions.
    *   **SMO Impact:**
        *   The `placement.py` and `scaling.py` modules will need major refactoring.
        *   **Interface for Prediction Input:** The scaling logic must be ableto accept predicted workload trends (from H3NI's ML models) as input, not just current Prometheus metrics.
        *   **Interface for Energy Parameters:** The placement logic must accept node/cluster energy characteristics.
        *   **Modify Optimization Models:** The Gurobi models (or their open-source replacements) will need to be updated to include these new predictive inputs and energy objectives/constraints.
        *   **Modular Decision Points:** SMO might need to expose well-defined internal functions that H3NI extensions can call to get "advice" or trigger parts of the decision process with new parameters.
        *   This might lead to a strategy pattern or plugin architecture for different scaling/placement policies within SMO.

2. **Enhanced API for Control and Feedback (Internal and External):**
    *   **H3NI Relevance:**
        *   Hop3 plugin communicates with SMO via REST and "potentially Python API".
        *   H3NI Orchestration Mechanisms "Consult" SMO Core.
    *   **SMO Impact:**
        *   **Python API (as discussed in point 1):** Needs to be well-defined and stable.
        *   **Richer REST API Payloads/Queries:** The existing REST API might need to expose more detailed status, resource information, or accept more nuanced placement/scaling parameters if Hop3 or H3NI needs them.
        *   **Internal "Consultation" API:** If H3NI extensions are tightly coupled (e.g., run in the same process space or as plugins), SMO needs clear internal interfaces for these extensions to query current state, capacities, or trigger parts of its decision-making logic.

3. **Data Ingestion/Adaptation for New Metrics:**
    *   **H3NI Relevance:** Energy-aware orchestration and ML-driven scaling will rely on new types of data not currently fetched by `PrometheusHelper` (e.g., node energy consumption, detailed workload characteristics for ML models).
    *   **SMO Impact:**
        *   `PrometheusHelper` might need to be extended, or new helper classes created, to fetch these new metrics.
        *   SMO needs to be able to process and utilize this new data in its decision algorithms.
        *   The schema for `Graph` or `Service` models might need to store new metadata related to these aspects if it's static or semi-static.

4. **Modular Extension Points for H3NI Mechanisms:**
    *   **H3NI Relevance:** "SMO Extension Development: Implement the new orchestration mechanisms ... as extensions to the SMO. ... Ensure a modular design...".
    *   **SMO Impact:** SMO might need a more formal "plugin" or "extension" architecture. This could involve:
        *   Defined interfaces that H3NI extensions must implement.
        *   Registration mechanisms for these extensions.
        *   Lifecycle management for extensions.
        *   This makes SMO a platform rather than just an application.

5.  **Support for Vertical Scaling (??):**
    *   **H3NI Relevance:** "Horizontal and Vertical Scaling" is listed as a functionality. SMO currently focuses on horizontal.
    *   **SMO Impact:**
        *   `KubeHelper` needs new methods to modify resource requests/limits of existing Kubernetes deployments/pods.
        *   SMO's scaling logic (likely a new component or significant modification to `scaling.py`) needs to decide *when* and *how* to scale vertically (e.g., based on sustained high CPU/memory pressure not solvable by horizontal scaling, or ML predictions).
        *   This might involve a new optimization model or heuristics.
        *   The interaction between horizontal and vertical scaling needs careful design.

### Already Done

1.  **Integration with Open-Source Solvers:**
    *   **H3NI Relevance:** "H3NI Orchestration Mechanisms" lists "Open-Source Solvers", and "Replace any proprietary optimization solvers with open-source alternatives".
    * This has been done in Q2 2025 by the NEPHELE Team so not our (Abilian) concern. Tests need to be updated though.

### Summary

This plan pushes SMO to become a more generic, configurable, and extensible orchestration *framework*, where the H3NI plugins will provide specialized intelligence and control mechanisms that leverage and enhance SMO's core capabilities, when integrated with Hop3.

*   **Prioritize Modularity:** Break down monoliths (global state, Flask coupling).
*   **Make Decision Logic Flexible:** The core placement and scaling algorithms are central. They need to become highly adaptable to new inputs (predictions, energy data) and new objectives. This is likely the biggest area of change.
*   **Embrace Extensibility:** Design for H3NI components to plug into SMO, either via a well-defined Python API or a more formal extension system.

