# SMO

> This is a forked version of the original Nephele SMO repository. The original repository is located at: https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/smo
> This is a work in progress. The development plan is outlined in the [TODO.md](./TODO.md) file.

Build status: [![builds.sr.ht status](https://builds.sr.ht/~sfermigier/smo-h3ni.svg)](https://builds.sr.ht/~sfermigier/smo-h3ni?)


## TOC

<!-- toc -->

- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Container/Artifact registry](#containerartifact-registry)
  * [Docker container images](#docker-container-images)
    + [Docker settings](#docker-settings)
    + [Containerd (Kubernetes) settings](#containerd-kubernetes-settings)
  * [OCI artifacts](#oci-artifacts)
- [Full example](#full-example)
- [File structure](#file-structure)
- [NFVCL API](#nfvcl-api)

<!-- tocstop -->

## REUSE Licence Check

```
# SUMMARY

* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: MIT, CC-BY-4.0, BSD-3-Clause
* Read errors: 0
* Files with copyright information: 123 / 123
* Files with license information: 123 / 123

Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
```

---

(Original README below)

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

## Prerequisites
The following assumptions are made:
- The Kubernetes cluster uses the containerd runtime as CRI
- Karmada and Submariner have been installed to the cluster
- The Prometheus CRDs need to be installed in the Karmada Control plane in order for the Service Monitors to work. If not installed,  either install them like this specifying the right version:
```bash
# Define the Prometheus Operator version
VERSION="v0.78.2"

# Base URL for the Prometheus Operator CRDs
BASE_URL="https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/$VERSION/example/prometheus-operator-crd"

# Kubeconfig file of the Karmada control plane
KUBECONFIG="~/.kube/karmada-apiserver.config"

# Apply each CRD with server-side apply
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_alertmanagerconfigs.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_alertmanagers.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_podmonitors.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_probes.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_prometheusagents.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_prometheuses.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_prometheusrules.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_scrapeconfigs.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_servicemonitors.yaml --kubeconfig $KUBECONFIG
kubectl apply --server-side -f $BASE_URL/monitoring.coreos.com_thanosrulers.yaml --kubeconfig $KUBECONFIG

# Create the monitoring namespace
kubectl create ns monitoring --kubeconfig $KUBECONFIG
```
or delete all `servicemonitor.yaml` files from all the helmcharts.

## Getting started
The config files inside the `config` directory contain: the database credentials, the Karmada config and the NFVCL URL
- The database credentials can be set to whatever the user prefers but the credentials in the `flask.env` and `postgres.env` files must match
- Regarding the Karmada config, the docker compose YAML mounts the `~/.kube` directory inside the container meaning that the SMO expects the karmada kubeconfig file to be inside that directory. Afterwards, the user can specify the name of the config file in the `KARMADA_KUBECONFIG` environment variable of the `config/flask.env` file.
- The NVFCL URL is optional and only relevant if the NFVCL API is used
- The `hdarctl` binary has to be available in the path. You can run for example:
    ```bash
    wget https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-development-sandbox/-/raw/main/tools/hdarctl
    sudo chmod u+x hdarctl
    sudo mv hdarctl /usr/local/bin
    ```

To deploy, use docker compose:
```bash
docker compose up
```
The SMO API is available by default at port 8000 and the Swagger API is accesible at the `/docs` endpoint (http://localhost:8000/docs)

## Container/Artifact registry
While the Nephele platform works with a Hyper-Distributed Application Registry (HDAR), for testing purposes we can run a Distribution container/artifact registry. A docker compose file is located inside the `registry` directory:
- Start up: `docker compose up -d`
- Tear down: `docker compose down -v`
The Distribution registry runs in port `5000` where container images and OCI artifacts can be pushed
### Docker container images
#### Docker settings
The registry can be used to host Docker images. For the container images to be accessible from Kubernetes, the images need to be tagged with the host's IP. Additionally the docker daemon has to be configured to communicate with the registry through HTTP. This can be done by adding:
```json
{
  "insecure-registries" : ["<Host-IP>:5000"]
}
```
to the `/etc/docker/daemon.json` file. Afterwards:
- Image creation:
    - New image creation: `docker build -t <Host-IP>:5000/<image-tag>`
    - Tag an already existing image: `docker tag <existing-image> <Host-IP>:5000/<image-tag>`
- Image push: `docker push <Host-IP>:5000/<image-tag>`
- Image pull: `docker pull <Host-IP>:5000/<image-tag>`

#### Containerd (Kubernetes) settings
Additionally, since Kubernetes uses containerd, we also need to configure it to use an insecure registry. We first modify `/etc/containerd/config.toml` and define a config path:
```toml
    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = "/etc/containerd/certs.d"
```
Then create the `/etc/containerd/certs.d` directory and inside it create two directories:
- `/etc/containerd/certs.d/docker.io/`
- `/etc/containerd/certs.d/<Host-IP>:5000/`

Then create the file `/etc/containerd/certs.d/docker.io/hosts.toml` with the content:
```toml
server = "https://registry-1.docker.io"
[host."https://{docker.mirror.url}"]
  capabilities = ["pull", "resolve"]
```
Finally, create the `/etc/containerd/certs.d/<Host-IP>:5000/hosts.toml` with the content:
```toml
server = "https://registry-1.docker.io"
[host."http://<Host-IP>:5000"]
  capabilities = ["pull", "resolve", "push"]
  skip_verify = true
```

### OCI artifacts
Helmchart artifacts can be created using the `hdarctl` tool that can be found [here](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-development-sandbox/-/raw/main/tools/hdarctl). The `hdarctl` tool can package Hyper-Distributed Application Graphs, VO helmcharts and Application helmcharts and also push them to the OCI registry.
- Package artifact: `hdarctl package tar <artifact-directory>`
- Push artifact under a specific project: `hdarctl push <artifact>-<version>.tar.gz http://localhost:5000/<project>`
- Install artifact with an arbitrary release name: `helm install <release-name> --plain-http oci://localhost:5000/<project>/<artifact>`

## Full example
A full example can be found in the `examples/brussels-demo` directory. The steps to deploy the example are:
1. Setup the Docker and Containerd daemons to use insecure registries as described [above](#docker-container-images)
2. Start the container/artifact registry `docker compose -f registry/docker-compose.yaml up -d`
3. Start the SMO in detached mode `docker compose up -d`
4. Cd to the `examples/brussels-demo` directory
5. Edit the Makefile with the proper IPs
6. Run `make push-images` to push the Docker images of the services to the registry
7. Run `make change-ips` to change th IPs of the helmcharts and the descriptor
8. Run `make push-artifacts` to push the helmcharts to the artifact registry
9. Change the variables inside the `create-existing-artifact.sh` bash script
10. Run the `create-existing-artifact.sh` bash script to request the Graph deployment from the SMO

To delete the graph run the `delete.sh` script.

## File structure
The directory structure of the codebase is as follows:
```
src/
├── errors
├── models
├── routes
├── services
├── utils
├── app.py
└── config.py
```
- `errors`: custom errors and handlers
- `models`: db models
- `routes`: app blueprints
- `services`: business logic for the routes
- `utils`: misc
- `app.py`: the Flask application
- `config.py`: the Flask application configuration files


## NFVCL API
To create a new Kubernetes Cluster using the NFVCL API using an Openstack-powered infrastructure:
- `POST` to `/smo_vims` a json like:
    ```json
    {
        "mgmt_network": {
            "cidr": "X.X.X.X/24",
            "gateway": "X.X.X.X",
            "name": "openstack_network_name"
        },
        "pop_area": 0,
        "service_network": {
            "cidr": "X.X.X.X/24",
            "gateway": "X.X.X.X",
            "name": "openstack_network_name"
        },
        "topology": "topology_name",
        "use_floating_ip": true,
        "vim_name": "vim_name",
        "vim_password": "openstack_password",
        "vim_tenant_name": "openstack_project",
        "vim_type": "openstack",
        "vim_url": "http://X.X.X.X:5000/v3",
        "vim_user": "openstack_user"
    }
    ```
- `POST` to `/clusters`:
    ```json
    {
        "pop_area": 0,
        "vim_name": "vim_name"
    }
    ```
After the above, the SMO will make requests to the NFVCL API to create a new Kubernetes cluster.
