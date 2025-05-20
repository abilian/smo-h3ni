# SMO Refactoring Plan

## Initial (already prototyped) ideas

Here are some refactoring tasks that we feel are needed or desirable, based on the refactoring work we've prototyped and the needs we have identified so far for H3NI:

1.  **Adopt a Standard Python Package Structure (e.g., `src/smo/`):**
    *   **Suggestion:** Reorganize the `src/` directory into a formal Python package (e.g., `src/smo/`), with sub-modules for different concerns (e.g., `smo.flask`, `smo.models`, `smo.services`).
    *   **Benefits:** This improves modularity, clarifies imports (e.g., `from smo.config import X` instead of `from config import X`), reduces potential naming conflicts, and makes the codebase easier to navigate and scale as it grows.

2.  **Introduce a Command-Line Interface (CLI):**
    *   **Suggestion:** Implement a CLI (e.g., using `argparse`) to expose core functionalities like deploying graphs, listing them, starting/stopping, etc.
    *   **Benefits:** Provides a powerful way to interact with the system for automation, scripting, and direct operational tasks without needing to go through the HTTP API for everything. This can also streamline development and testing workflows.

3.  **Formalize Flask Extensions Management:**
    *   **Suggestion:** Initialize extensions like SQLAlchemy (`db`) in a dedicated module (e.g., `smo.extensions.py`) and use `init_app()` within the `create_app` factory.
    *   **Benefits:** This is a common Flask pattern that helps avoid circular dependencies and makes the app structure cleaner, especially as more extensions might be added.

4.  **Enhance Model Definitions:**
    *   **Suggestion:**
        *   Use `sqlalchemy.JSON` for better database portability than `JSONB` (if broader DB support is a future goal).
        *   Introduce Enums (e.g., `GraphStatus`, `ServiceStatus`) for status fields.
        *   Add methods directly to models for state changes (e.g., `graph.start()`, `service.deploy()`).
    *   **Benefits:** Enums make status fields more robust, readable, and less prone to typos. Encapsulating state-changing logic within the models themselves improves object-oriented design.

5.  **Systematically Add Type Hinting and Docstrings:**
    *   **Suggestion:** Integrate comprehensive type hints and detailed docstrings throughout the codebase.
    *   **Benefits:** Significantly improves code readability and understandability, making it easier to onboard new team members. Type hints enable static analysis tools (like MyPy) to catch potential bugs early in the development cycle.

6.  **Implement a Comprehensive Test Suite:**
    *   **Suggestion:** Create a `tests/` directory with unit tests for core logic (like placement utilities), integration tests for API endpoints, and architectural tests (e.g., using `pytest-archon` to ensure modules don't import things they shouldn't). Use a test-friendly database like SQLite for faster test runs.
    *   **Benefits:** This is crucial for ensuring code correctness, preventing regressions when making changes, and giving developers confidence to refactor. Tests also serve as living documentation.

7.  **Introduce Database Migrations (e.g., Alembic):**
    *   **Suggestion:** Integrate Alembic to manage database schema changes.
    *   **Benefits:** Provides a version-controlled, repeatable way to evolve the database schema, which is essential for production deployments and team collaboration.

8.  **Adopt Modern Developer Tooling (e.g., Nox, `uv`):**
    *   **Suggestion:** Use a tool like `nox` to automate common development tasks (linting, testing across Python versions, security checks) and consider `uv` for faster dependency management.
    *   **Benefits:** Enforces code quality, ensures consistency across developer environments, and speeds up the development feedback loop.

9.  **Standardize WSGI Entry Point:**
    *   **Suggestion:** Add a `wsgi.py` file to serve as the standard entry point for WSGI servers (like Gunicorn).
    *   **Benefits:** Aligns with best practices for deploying Flask applications in production.

10. **Increase Robustness in External Process Calls:**
    *   **Suggestion:** Ensure `subprocess.run` calls (e.g., for `helm`, `hdarctl`) consistently use `check=True` to raise exceptions on failure, and ensure critical exceptions are re-raised or handled appropriately.
    *   **Benefits:** Makes the application more resilient by ensuring failures in external tools are immediately caught and surfaced, rather than potentially failing silently.


## Additional Ideas

Here are additional areas where the SMO codebase could be further refined to enhance its architecture and prepare it for more complex scenarios (→ more modular, configurable, and testable system):

11. **Decouple Business Logic from Flask (`services` layer):**
    *   **Suggestion:** Ensure the `smo.services` modules (like `graph_service.py`) have minimal direct dependencies on Flask concepts (`current_app`, `request`). Instead, necessary Flask-specific data should be passed in as arguments from the route handlers.
    *   **Benefits:**
        *   Makes the core business logic highly testable in isolation, without needing a Flask app context.
        *   Allows the core logic to be potentially reused in other contexts (e.g., the CLI, background workers) without pulling in Flask.
        *   The architecture test `Services should not import flask` (currently skipped) aims for this.

12. **Eliminate Global State (Especially in `graph_service.py`):**
    *   **Suggestion:** Refactor to remove global variables like `graph_placement`, `background_scaling_threads`, and `stop_events`.
        *   Consider encapsulating graph-specific state (like `graph_placement`) within the `Graph` model or a dedicated state management class associated with a graph instance.
        *   Manage background tasks and their stop events through a dedicated manager class or service that can be instantiated and controlled per graph or application instance.
    *   **Benefits:**
        *   Greatly improves testability, as state is no longer shared implicitly.
        *   Makes the application more robust, especially if considering multi-process or multi-threaded web servers (global state can lead to race conditions or unexpected behavior).
        *   Simplifies reasoning about the application's state at any given time.

13. **Externalize Configuration and Constants:**
    *   **Suggestion:** Move hardcoded values from `utils/constant.py` (service names, cluster details, algorithm parameters) into:
        *   The graph descriptor itself (for graph-specific parameters).
        *   Application configuration files (e.g., YAML, TOML) that can be loaded at runtime.
        *   Environment variables for deployment-specific settings.
    *   **Benefits:**
        *   Massively increases flexibility and adaptability to different environments and use cases without code changes.
        *   Makes the system data-driven rather than code-driven for these aspects.
        *   Simplifies updates to these parameters.

14. **Introduce Dependency Injection:**
    *   **Suggestion:** Instead of services or helpers directly instantiating their dependencies (e.g., `KubeHelper`, `PrometheusHelper`), consider injecting these dependencies, perhaps during the initialization of service classes or via the application factory.
    *   **Benefits:**
        *   Enhances testability by allowing easy mocking of dependencies.
        *   Improves decoupling between components.
        *   Makes it easier to swap out implementations (e.g., a different Kubernetes interaction library).

15. **Refine Error Handling and Define Custom Exceptions:**
    *   **Suggestion:**
        *   Define custom, domain-specific exceptions (e.g., `GraphNotFoundError`, `PlacementError`, `HelmCommandError`) that can be raised from the service layer.
        *   Map these custom exceptions to appropriate HTTP error responses in the Flask error handlers.
    *   **Benefits:**
        *   Provides more meaningful error information to clients and logs.
        *   Decouples the service layer from specific HTTP status codes.
        *   Makes error handling logic clearer and more centralized.

16. **Abstract External Tool Interactions:**
    *   **Suggestion:** Create clearer abstractions or wrapper classes around external CLI tools like `hdarctl` and `helm`. The current `helm_install_artifact` is a good start, but this could be expanded.
    *   **Benefits:**
        *   Isolates the system from the specifics of these tools.
        *   Makes it easier to mock these interactions for testing.
        *   If a tool's CLI changes or a different tool is chosen, the impact on the codebase is localized.

17. **Asynchronous Task Management:**
    *   **Suggestion:** For long-running operations like graph deployment or triggering placement (which involves Helm and potentially Gurobi), consider using a proper asynchronous task queue (e.g., Celery, RQ, or even `asyncio` with `aiohttp` if the whole app moves that way).
        *   The current `threading` for scaling is a good first step but might be insufficient for more demanding background tasks.
    *   **Benefits:**
        *   Prevents blocking API requests, improving responsiveness.
        *   Provides better mechanisms for retries, monitoring, and managing background work.
        *   Can improve scalability by offloading work from web server processes.

18. **Make Placement and Scaling Algorithms More Configurable/Pluggable:**
    *   **Suggestion:** While complex, consider designing the placement and scaling decision logic (`decide_placement`, `decide_replicas`) in a way that different strategies or Gurobi model variations could be configured or even plugged in.
    *   **Benefits:** Allows adaptation to different optimization goals or constraints without rewriting the core service logic. This is a more advanced refactoring.

19. **Review Database Interactions for Efficiency and Transactions:**
    *   **Suggestion:**
        *   Ensure database queries are efficient, especially in performance-sensitive paths.
        *   Wrap sequences of database operations that should be atomic within explicit transactions (`with db.session.begin():`).
    *   **Benefits:** Improves performance and data integrity.

20. **Adopt RESTful Principles for State-Changing Operations:**
    *   **Suggestion:** Revisit API routes that modify state (e.g., start, stop, placement) to use appropriate HTTP methods (POST, PUT, PATCH, DELETE) instead of GET.
    *   **Benefits:** Aligns with REST best practices, making the API more predictable and semantically correct. Prevents accidental state changes from simple browser navigation or caching.
