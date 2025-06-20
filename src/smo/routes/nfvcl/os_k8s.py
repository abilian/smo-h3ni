"""Openstack cluster endpoints."""

from __future__ import annotations

from flasgger import swag_from
from flask import Blueprint, request, current_app

from smo.services.nfvcl.os_k8s_service import (
    fetch_all_clusters,
    create_cluster,
    fetch_cluster,
    remove_cluster,
    scale_out_cluster,
    sync,
)

os_k8s = Blueprint("os_k8s", __name__, url_prefix="/os_k8s")


@os_k8s.route("/clusters", methods=["GET"])
@swag_from("swagger/os_k8s/get_os_k8s_clusters.yaml")
def get_os_k8s_clusters():
    """Fetches all Openstack Kubernetes clusters."""

    return fetch_all_clusters(), 200


@os_k8s.route("/clusters", methods=["POST"])
@swag_from("swagger/os_k8s/post_os_k8s.yaml")
def post_os_k8s():
    """Creates a new Openstack Kubernetes cluster."""

    nfvcl_base_url = current_app.config["NFVCL_BASE_URL"]
    data = request.json

    return create_cluster(nfvcl_base_url, data), 201


@os_k8s.route("/cluster/<string:smo_id>", methods=["GET"])
@swag_from("swagger/os_k8s/get_os_k8s.yaml")
def get_os_k8s(smo_id):
    """Fetches the Openstack Kubernetes cluster with the specified id."""

    return fetch_cluster(smo_id), 200


@os_k8s.route("/cluster/<string:smo_id>", methods=["DELETE"])
@swag_from("swagger/os_k8s/delete_os_k8s.yaml")
def delete_os_k8s(smo_id):
    """Delete the Openstack Kubernetes cluster with the specified id."""

    nfvcl_base_url = current_app.config["NFVCL_BASE_URL"]
    return remove_cluster(nfvcl_base_url, smo_id), 200


@os_k8s.route("/scale-out/<string:smo_id>", methods=["POST"])
@swag_from("swagger/os_k8s/scale_out_k8s.yaml")
def scale_out(smo_id):
    """Scale out the Openstack Kubernetes cluster with the specified id."""

    nfvcl_base_url = current_app.config["NFVCL_BASE_URL"]
    return scale_out_cluster(nfvcl_base_url, smo_id), 200


@os_k8s.route("/sync/nfvcl_k8s", methods=["POST"])
@swag_from("swagger/os_k8s/sync_nfvcl.yaml")
def sync_nfvcl():
    """Sync information from the NFVCL instance."""

    nfvcl_base_url = current_app.config["NFVCL_BASE_URL"]
    pop_area = request.args.get("pop_area")
    return sync(nfvcl_base_url, pop_area), 200
