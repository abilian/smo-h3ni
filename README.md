# SMO

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

## Getting started
Use docker compose:
```bash
docker compose up
```
The SMO API is available at port 8000.

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
