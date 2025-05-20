# A Tour of the Orignal SMO Codebase

This Python codebase implements a Flask-based API service (SMO-API) designed to manage, deploy, and auto-scale "application graphs" across Kubernetes clusters, potentially federated using Karmada.

This analysis is based on the code base at the following commit:

```
commit 832d6e65b869007a548d51b989163d1ad0bb0be0
Merge: 3d9abe2 c0b4ddd
Author: Nikos Filinis <nfilinis@netmode.ntua.gr>
Date:   Thu Jun 27 16:48:25 2024 +0000
```

## Overall Architecture

The application follows a common web service architecture:

1.  **API Layer (`src/app.py`, `src/routes/`)**: Exposes HTTP endpoints using Flask. Flasgger is used for Swagger/OpenAPI documentation.
2.  **Configuration (`src/config.py`)**: Manages environment-specific settings (dev, prod) and loads secrets/configurations using `python-dotenv`.
3.  **Business Logic (`src/services/graph_service.py`)**: Contains the core logic for graph deployment, placement decisions, lifecycle management (start/stop), and initiating auto-scaling.
4.  **Data Model & Persistence (`src/models/`)**: Defines data structures (Graph, Service) using SQLAlchemy and interacts with a PostgreSQL database.
5.  **Utility Modules (`src/utils/`)**:
    *   `constant.py`: Stores (mostly hardcoded) constants for services, clusters, and algorithm parameters.
    *   `kube_helper.py`: Interacts with Kubernetes clusters (get/scale deployments).
    *   `placement.py`: Implements the service placement algorithm using Gurobi.
    *   `prometheus_helper.py`: Fetches metrics from Prometheus.
    *   `scaling.py`: Implements the replica auto-scaling algorithm using Gurobi and Prometheus metrics.
6.  **Error Handling (`src/errors/error_handlers.py`)**: Defines custom handlers for specific exceptions.

## File-by-File Analysis

*   **`src/app.py`**:
    *   **Purpose**: Main Flask application entry point.
    *   **Functionality**: Initializes the Flask app, sets up Swagger, loads configuration based on `FLASK_ENV`, registers blueprints (for routes like `graph`), custom error handlers, and initializes the SQLAlchemy database (including `db.create_all()`).
    *   **Key Libraries**: Flask, Flasgger, SQLAlchemy.

*   **`src/config.py`**:
    *   **Purpose**: Manages application configurations.
    *   **Functionality**: Defines a base `Config` class and environment-specific classes (`ProdConfig`, `DevConfig`). Loads database credentials and Karmada kubeconfig path from environment variables (via `.env` file).
    *   **Notes**: `KARMADA_KUBECONFIG` path has a hardcoded directory prefix.

*   **`src/errors/error_handlers.py`**:
    *   **Purpose**: Defines custom error handlers for Flask.
    *   **Functionality**: Provides JSON responses for `subprocess.CalledProcessError` and `yaml.YAMLError`, both returning HTTP 500.

*   **`src/models/__init__.py`**:
    *   **Purpose**: Initializes the SQLAlchemy `db` instance and aggregates model imports.
    *   **Functionality**: Creates `db = SQLAlchemy()` and imports `Graph` and `Service` models.

*   **`src/models/graph.py`**:
    *   **Purpose**: Defines the `Graph` SQLAlchemy model.
    *   **Functionality**: Represents an application graph with attributes like name, status, project, Grafana URL, and the graph descriptor (as JSONB). It has a one-to-many relationship with `Service` (services are deleted if the graph is deleted). Includes a `to_dict()` method for serialization.

*   **`src/models/service.py`**:
    *   **Purpose**: Defines the `Service` SQLAlchemy model.
    *   **Functionality**: Represents a service node within a graph, with attributes like name, status, cluster affinity, artifact details, resource requirements (JSONB), and Helm values overrides (JSONB). It has a many-to-one relationship with `Graph`. Includes a `to_dict()` method.
    *   **Note**: `name = db.Column(db.String(255), unique=True, nullable=False)` implies service names must be globally unique, not just unique within a graph. This might be a design constraint or an oversight.

*   **`src/routes/graph.py`**:
    *   **Purpose**: Defines API routes related to application graphs.
    *   **Functionality**: Implements endpoints for:
        *   `GET /graph/project/<project>`: List graphs in a project.
        *   `POST /graph/project/<project>`: Deploy a new graph (accepts artifact URL or direct YAML/JSON descriptor).
        *   `GET /graph/<name>`: Get details of a specific graph.
        *   `DELETE /graph/<name>`: Remove a graph.
        *   `GET /graph/<name>/placement`: Trigger placement algorithm.
        *   `GET /graph/<name>/start`: Start a stopped graph.
        *   `GET /graph/<name>/stop`: Stop a running graph.
    *   **Notes**:
        *   Uses `swag_from` for API documentation.
        *   The `deploy` endpoint's logic for handling `request_data` when it's not an artifact (i.e., `yaml.safe_load(request_data)` where `request_data` is from `request.get_json()`) appears problematic if `request_data` is a Python dictionary. `yaml.safe_load` expects a string or stream.
        *   Using GET for state-changing actions (start, stop, placement) is not strictly RESTful but is a common practice for simplicity.

*   **`src/services/graph_service.py`**:
    *   **Purpose**: Contains the core business logic for graph management.
    *   **Functionality**:
        *   Deploys graphs by processing descriptors, deciding initial placement, and using Helm to install services.
        *   Manages graph lifecycle (start, stop, remove), interacting with Helm.
        *   Triggers re-placement calculations.
        *   Retrieves graph descriptors from artifacts (using `hdarctl` CLI).
        *   Spawns background threads (`scaling_loop`) for auto-scaling services on each cluster.
    *   **Notes**:
        *   Uses global variables (`graph_placement`, `background_scaling_threads`, `stop_events`), which can be problematic for scalability and testing.
        *   Relies on external CLIs: `hdarctl` and `helm`. `subprocess.run` calls for Helm don't use `check=True`, so failures might not be propagated as exceptions unless Helm itself exits non-zero.
        *   The `spawn_scaling_processes` function has a fixed size for `background_scaling_threads` and `stop_events` (2), limiting scaling to two clusters regardless of `CLUSTERS` constant.
        *   `trigger_placement` uses a global `SERVICES` constant instead of the specific graph's services for `get_replicas`.
        *   Hardcoded logic for `voChartOverwrite` and `implementer == 'WOT'`.

*   **`src/utils/constant.py`**:
    *   **Purpose**: Stores constant values.
    *   **Functionality**: Defines lists and dictionaries for service names, cluster details (capacity, acceleration), CPU limits, default replicas, scaling parameters (ALPHA, BETA for service capacity modeling), Prometheus/Grafana URLs, etc.
    *   **Notes**: Highly hardcoded, limiting flexibility. The comment "To be replaced in the future" indicates this is known.

*   **`src/utils/kube_helper.py`**:
    *   **Purpose**: Helper class for Kubernetes API interactions.
    *   **Functionality**: Uses the `kubernetes` Python client to get replica counts, CPU limits, and scale deployments.
    *   **Notes**: `scale_deployment` has a general `except Exception` that prints the error but doesn't re-raise, potentially hiding issues.

*   **`src/utils/placement.py`**:
    *   **Purpose**: Implements the service placement algorithm.
    *   **Functionality**: Uses Gurobi to solve an optimization problem that decides which cluster each service should be placed on, considering cluster capacities, service requirements, acceleration features, and minimizing deployment/re-optimization costs.
    *   **Notes**: Contains hardcoded assumptions in the Gurobi model (e.g., `s0` on `E1`, dependency structure `d = [0,0]`).

*   **`src/utils/prometheus_helper.py`**:
    *   **Purpose**: Helper class for querying Prometheus.
    *   **Functionality**: Constructs and executes PromQL queries to get service latency, request rate, and CPU utilization.
    *   **Notes**: Handles `NaN` results from Prometheus by returning default values.

*   **`src/utils/scaling.py`**:
    *   **Purpose**: Implements the replica auto-scaling algorithm.
    *   **Functionality**:
        *   `scaling_loop`: Runs periodically in a background thread for each managed cluster. Fetches metrics from Prometheus, current state from Kubernetes.
        *   `decide_replicas`: Uses Gurobi to determine the optimal number of replicas for services on a cluster, considering request rates, service capacity models (alpha, beta), CPU limits, and cluster capacity. Aims to minimize resource utilization and scaling costs.
        *   If Gurobi can't find a scaling solution, it triggers a re-placement by making an HTTP call to its own API (`http://localhost:8000/graph/{graph_name}/placement`).
    *   **Notes**:
        *   The `localhost:8000` call is a tight coupling and might fail in containerized environments.
        *   Contains a very specific hardcoded rule in `scaling_loop` for determining `request_rates` for `image-compression-vo` based on `noise-reduction`.

## Strengths

*   **Modular Structure**: The codebase is generally well-organized into logical components.
*   **Use of Optimization**: Leverages Gurobi for complex placement and scaling decisions, which can lead to efficient resource utilization if models are accurate.
*   **API Documentation**: Flasgger integration provides a good starting point for API discoverability.
*   **Asynchronous Scaling**: Background threads for scaling prevent blocking of API requests.
*   **Clear Configuration Management**: Separation of configuration for different environments.

**Weaknesses and Areas for Improvement:**

1.  **Extensive Hardcoding**: Many critical parameters, service names, cluster details, and algorithm assumptions are hardcoded in `utils/constant.py` and throughout the logic. This severely limits flexibility and reusability.
    *   **Recommendation**: Externalize configurations (e.g., via graph descriptors, API-configurable settings, or dedicated configuration files).
2.  **Global State Management**: Use of global variables (e.g., `graph_placement`, `background_scaling_threads`) makes the application harder to test, debug, and scale (especially with multi-process workers).
    *   **Recommendation**: Encapsulate state in classes or manage it via Flask's application context or dependency injection.
3.  **Error Handling and Robustness**:
    *   Some subprocess calls (e.g., Helm) lack `check=True`, potentially masking failures.
    *   `KubeHelper`'s `scale_deployment` catches and prints exceptions but doesn't re-raise.
    *   The `deploy` route in `src/routes/graph.py` has a potential bug with `yaml.safe_load` for direct JSON descriptors.
    *   **Recommendation**: Implement more robust error checking and propagation.
4.  **Fixed Limits and Assumptions**:
    *   Scaling logic seems limited to two clusters due to fixed-size thread/event lists.
    *   Placement and scaling algorithms have hardcoded assumptions about service names (e.g., 's0') and inter-service relationships.
    *   `Service.name` global uniqueness constraint.
    *   **Recommendation**: Make these dynamic and configurable.
5.  **Tight Coupling**: The scaling module's fallback mechanism (HTTP call to `localhost:8000`) is a strong internal coupling.
    *   **Recommendation**: Refactor to direct function calls or an internal event system.
6.  **Testability**: The current heavy reliance on global state, external CLIs, and hardcoded values makes unit and integration testing difficult.
    *   **Recommendation**: Design for testability using techniques like dependency injection and mocking.
7.  **REST API Design**: GET requests are used for operations that modify state (start, stop, placement).
    *   **Recommendation**: Consider using POST or PUT for these actions for stricter REST compliance.
8.  **Database Operations**: Long-running operations involving database commits and external calls (like Helm deployments) might need more sophisticated transaction management or sagas for atomicity/rollback.

## Conclusion

The SMO-API codebase provides a sophisticated foundation for managing and auto-scaling application graphs. It leverages powerful tools like Flask, SQLAlchemy, and Gurobi. However, its most significant challenge is the pervasive hardcoding and reliance on global state, which hinder its flexibility, scalability, and maintainability. Addressing these issues by making the system more data-driven and configurable would greatly enhance its robustness and applicability to a wider range of scenarios.
