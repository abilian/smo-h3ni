# SMO

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

## Getting started
The config files inside the `config` directory contain: the database credentials, the Karmada config and the NFVCL URL
- The database credentials can be set to whatever the user prefers but the credentials in the `flask.env` and `postgres.env` files must match
- Regarding the Karmada config, the docker compose YAML mounts the `~/.kube` directory inside the container meaning that the SMO expects the karmada kubeconfig file to be inside that directory. Afterwards, the user can specify the name of the config file in the `KARMADA_KUBECONFIG` environment variable of the `config/flask.env` file.
- The NVFCL URL is optional and only relevant if the NFVCL API is used

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
6. Run `make push-images`
7. Change the `image` URL from `image: 10.0.3.53:5000/<image>:latest` to `image: <Host-IP>:5000/<image>:latest` in the:
    - `examples/brussels-demo/image-compression-vo/templates`
    - `examples/brussels-demo/image-detection/templates`
    - `examples/brussels-demo/noise-reduction/templates`
8. Change the `ociImage` URL in the `examples/brussels-demo/hdag` for all the services from `ociImage: "oci://10.0.3.53:5000/test/<service>"` to `ociImage: "oci://<Host-IP>:5000/test/<service>"`
9. Run `make push-artifacts`
10. Change the variables inside the `create-existing-artifact.sh` bash script
11. Run the `create-existing-artifact.sh` bash script to request the Graph deployment from the SMO

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
