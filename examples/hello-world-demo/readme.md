# "Hello World" Demo for SMO

This project provides a minimal "Hello World" example to demonstrate the core mechanics of deploying a hyper-distributed application using the Synergetic Meta-Orchestrator (SMO). It strips away the complexity of multi-service applications (like the "Brussels Demo") to focus on the essential workflow:

1.  Containerizing a simple Flask application.
2.  Defining the application as a Helm chart.
3.  Describing the application graph (HDAG) for the SMO.
4.  Using a `Makefile` to automate building, packaging, and pushing all required artifacts.
5.  Deploying the application graph to the SMO via a script.

## Layout

```
.
├── hdag/
│   └── hdag.yaml                   # The HDAG descriptor for our single-service app
├── hello-world/                    # The Helm chart for the "Hello World" app
│   ├── Chart.yaml
│   ├── templates/
│   │   ├── _helpers.tpl
│   │   ├── deployment.yaml
│   │   ├── propagationpolicy.yaml
│   │   ├── service.yaml
│   │   └── serviceexport.yaml
│   └── values.yaml
├── src/
│   └── hello-world/                # Source code for the Flask application
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
├── create-existing-artifact.sh     # Script to deploy the graph via SMO API
├── delete.sh                       # Script to delete the graph via SMO API
├── Makefile                        # Automation for building and pushing artifacts
└── README.md                       # This file
```

-   **hdag**: Contains the Hyper Distributed Application Graph (HDAG) descriptor that tells SMO about our application.
-   **hello-world**: Contains the Helm chart for deploying our simple Flask application.
-   **src**: Contains the Python source code and `Dockerfile` for the application.
-   **create-existing-artifact.sh**: A script that sends a POST request to the SMO to deploy the graph.
-   **delete.sh**: A script to delete the deployed graph.
-   **Makefile**: A helper to automate the build and push process.

## Instructions

This demo uses a `Makefile` to simplify the preparation and deployment process.

> ### ⚠️ Warning
> Before you begin, you **must** edit the `Makefile` and change the `HOST_IP` variable to the actual IP address of your host machine where the Docker registry will be accessible.

### 1. Build and Push Docker Image

This command builds the Docker image for the Flask application and pushes it to your local registry.

```bash
make push-images
```

### 2. Prepare and Push Artifacts

This command performs two key steps:

1.  It runs `make change-ips`, which updates the Helm chart and HDAG descriptor with your specified `HOST_IP`.
2.  It packages the Helm chart and the HDAG descriptor into OCI-compliant `.tar.gz` artifacts using `hdarctl`.
3.  It pushes these artifacts to your local registry.

```bash
make push-artifacts
```

### 3. Deploy the Application Graph

Run the deployment script. This sends a request to the SMO, telling it to pull the `hello-world-graph` artifact from your registry and deploy it.

```bash
./create-existing-artifact.sh
```

If successful, the SMO will use Karmada to deploy the "Hello World" application to one of the available clusters based on its placement logic.

### 4. Clean Up

To delete the deployed application graph from the SMO, run the delete script.

```bash
./delete.sh
```
