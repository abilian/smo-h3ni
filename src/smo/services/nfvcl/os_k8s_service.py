"""Openstack cluster business logic."""

from __future__ import annotations

import requests
from werkzeug.exceptions import InternalServerError, NotFound

from smo.models import VIM, OS_K8S_cluster, db


def fetch_all_clusters():
    try:
        os_k8s_clusters = db.session.query(OS_K8S_cluster).all()
        os_k8s_clusters_list = [k8s.as_dict() for k8s in os_k8s_clusters]
        if os_k8s_clusters_list:
            return os_k8s_clusters_list
        else:
            return "No Registered OS_K8S Clusters"

    except Exception as e:
        raise InternalServerError(
            str(e)
        )  # Return an error response if the request fails


def create_cluster(nfvcl_base_url, data):
    pop_area = data.get("pop_area")
    vim_name = data.get("vim_name")

    # Search the database for the corresponding VIM
    vim = db.session.query(VIM).filter_by(vim_name=vim_name, pop_area=pop_area).first()
    if not vim:
        raise NotFound("VIM not found")

    # Construct the request body for the NFVCL API
    nfvcl_request_body = {
        "areas": [
            {
                "area_id": pop_area,
                "is_master_area": True,
                "mgmt_net": vim.mgmt_network,
                "additional_networks": [vim.service_network],
                "service_net_required_ip_number": 20,
                "worker_replicas": 1,
            }
        ]
    }

    try:
        # Make a POST request to the NFVCL API
        response = requests.post(
            f"{nfvcl_base_url}/nfvcl/v2/api/blue/k8s", json=nfvcl_request_body
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
        nfvcl_response = response.json()

        # # Message response to identify the nfvcl ID
        detail_with_id = nfvcl_response["detail"]
        blueprint_id = detail_with_id.split("Blueprint ")[1].split()[0]
        print("Blueprint ID:", blueprint_id)

        # Create a new os_k8s_cluster instance and save it to the database
        os_k8s_cluster = OS_K8S_cluster(
            nfvcl_id=blueprint_id,
            pop_area=pop_area,
            # vim_name=vim_name,
            mgmt_network=vim.mgmt_network,
            service_network=vim.service_network,
        )
        db.session.add(os_k8s_cluster)
        db.session.commit()

        return {
            "message": "OS K8S cluster created successfully",
            "NFVCL_Response": nfvcl_response,
        }

    except requests.exceptions.RequestException as e:
        raise InternalServerError(str(e))


def fetch_cluster(smo_id):
    os_k8s_cluster = db.session.query(OS_K8S_cluster).filter_by(smo_id=smo_id).first()
    if not os_k8s_cluster:
        raise NotFound("OS_K8S cluster not found")
    return os_k8s_cluster.as_dict()


def remove_cluster(nfvcl_base_url, smo_id):
    # Find the OS_K8S_cluster by smo_id and delete it from the database
    os_k8s_cluster = db.session.query(OS_K8S_cluster).filter_by(smo_id=smo_id).first()
    if not os_k8s_cluster:
        raise NotFound("OS K8S cluster not found")
    # Delete the corresponding blueprint in the NFVCL API
    if os_k8s_cluster.nfvcl_id:
        try:
            response = requests.delete(
                f"{nfvcl_base_url}/nfvcl/v2/api/blue/{os_k8s_cluster.nfvcl_id}"
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Continue with the deletion of the OS_K8S_cluster
        except requests.exceptions.RequestException as e:
            raise InternalServerError(f"Failed to delete blueprint in NFVCL API: {e!s}")

    # Remove the OS_K8S_cluster from the database
    db.session.delete(os_k8s_cluster)
    db.session.commit()

    return {"message": "OS K8S cluster deleted successfully"}


def scale_out_cluster(nfvcl_base_url, smo_id):
    # Query the database to find the corresponding OS_K8S_cluster
    os_k8s_cluster = db.session.query(OS_K8S_cluster).filter_by(smo_id=smo_id).first()
    if not os_k8s_cluster:
        raise NotFound("OS K8S cluster not found")

    # Extract the nfvcl_id from the found cluster
    nfvcl_id = os_k8s_cluster.nfvcl_id

    # Construct the request body for the NFVCL API call
    request_body = {
        "areas": [
            {
                "area_id": os_k8s_cluster.pop_area,
                "is_master_area": False,
                "mgmt_net": os_k8s_cluster.mgmt_network,
                "service_net": os_k8s_cluster.service_network,
                "worker_replicas": 1,
            }
        ]
    }

    try:
        # Make a POST request to the NFVCL API
        response = requests.post(
            f"{nfvcl_base_url}/nfvcl/v2/api/blue/k8s/add_node?blue_id={nfvcl_id}",
            json=request_body,
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

        # Handle the response and return the appropriate message
        return {"message": "Node added to k8s cluster successfully"}

    except requests.exceptions.RequestException as e:
        raise InternalServerError(str(e))


def sync(nfvcl_base_url, pop_area):
    blue_data = fetch_blue_data(nfvcl_base_url)
    filtered_blue_data = filter_blue_data(blue_data, pop_area)

    added_nfvcl_k8s, updated_nfvcl_k8s, existing_nfvcl_ids = sync_nfvcl_k8s(
        filtered_blue_data
    )

    deleted_nfvcl_k8s = delete_stale_nfvcl_k8s(existing_nfvcl_ids)

    response_messages = []
    if added_nfvcl_k8s:
        response_messages.append({
            "message": "New Openstack k8s added successfully",
            "added_nfvcl_k8s": added_nfvcl_k8s,
        })
    if updated_nfvcl_k8s:
        response_messages.append({
            "message": "Existing Openstack k8s updated successfully",
            "updated_nfvcl_k8s": updated_nfvcl_k8s,
        })
    if deleted_nfvcl_k8s:
        deleted_ids = [k8s.smo_id for k8s in deleted_nfvcl_k8s]
        response_messages.append({
            "message": "Deleted Openstack k8s successfully",
            "deleted_nfvcl_k8s": deleted_ids,
        })
    if not response_messages:
        response_messages.append({"message": "Openstack k8s are already synced..."})

    return response_messages


def delete_stale_nfvcl_k8s(existing_nfvcl_ids):
    deleted_nfvcl_k8s = (
        db.session.query(OS_K8S_cluster)
        .filter(~OS_K8S_cluster.nfvcl_id.in_(existing_nfvcl_ids))
        .all()
    )
    for deleted_k8s in deleted_nfvcl_k8s:
        db.session.delete(deleted_k8s)
        db.session.commit()
    return deleted_nfvcl_k8s


def sync_nfvcl_k8s(blue_data):
    added_nfvcl_k8s = []
    updated_nfvcl_k8s = []
    existing_nfvcl_ids = set()

    for blue in blue_data:
        existing_nfvcl_ids.add(blue["id"])
        existing_blue = (
            db.session.query(OS_K8S_cluster)
            .filter_by(nfvcl_id=blue.get("id", ""))
            .first()
        )

        if existing_blue is None:
            # Add a new entry if it doesn't exist
            k8s = OS_K8S_cluster(
                nfvcl_id=blue["id"],
                pop_area=blue["state"]["master_area"]["area_id"],
                master_flavor=blue["create_config"]["master_flavors"],
                mgmt_network=blue["state"]["master_area"]["mgmt_net"],
                service_network=blue["state"]["master_area"]["service_net"],
                running_workers=blue["state"]["progressive_worker_number"],
            )
            db.session.add(k8s)
            db.session.commit()
            added_nfvcl_k8s.append(k8s.as_dict())  # Include ID in the response

        # Check for changes in each field
        elif (
            existing_blue.pop_area != blue["state"]["master_area"]["area_id"]
            or existing_blue.master_flavor != blue["create_config"]["master_flavors"]
            or existing_blue.mgmt_network != blue["state"]["master_area"]["mgmt_net"]
            or existing_blue.service_network
            != blue["state"]["master_area"]["service_net"]
            or existing_blue.running_workers
            != blue["state"]["progressive_worker_number"]
        ):
            # Update existing entry if any field has changed
            existing_blue.pop_area = blue["state"]["master_area"]["area_id"]
            existing_blue.master_flavor = blue["create_config"]["master_flavors"]
            existing_blue.mgmt_network = blue["state"]["master_area"]["mgmt_net"]
            existing_blue.service_network = blue["state"]["master_area"]["service_net"]
            existing_blue.running_workers = blue["state"]["progressive_worker_number"]
            updated_nfvcl_k8s.append(existing_blue.as_dict())
            db.session.commit()

    return added_nfvcl_k8s, updated_nfvcl_k8s, existing_nfvcl_ids


def fetch_blue_data(nfvcl_base_url):
    try:
        response = requests.get(nfvcl_base_url + "/nfvcl/v2/api/blue/?detailed=true")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch blue data: {e}")


def filter_blue_data(blue_data, pop_area):
    if pop_area:
        return [
            blue
            for blue in blue_data
            if blue["state"]["master_area"]["area_id"] == pop_area
        ]
    else:
        return blue_data
