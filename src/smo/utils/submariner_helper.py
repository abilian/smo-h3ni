"""Submariner helper class and utility functions."""

from __future__ import annotations

from kubernetes import client, config


class SubmarinerHelper:
    """Submariner helper class."""

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        config.load_kube_config(config_file=self.config_file_path)

        self.custom_client = client.CustomObjectsApi()

    def get_cluster_info(self):
        group = "submariner.io"
        version = "v1"
        namespace = "submariner-k8s-broker"
        plural = "clusters"

        response = self.custom_client.list_namespaced_custom_object(
            group, version, namespace, plural
        )

        result = {}
        for item in response.get("items", []):
            cluster_id = item["spec"]["cluster_id"]
            pod_cidr = item["spec"]["cluster_cidr"][0]
            service_cidr = item["spec"]["service_cidr"][0]

            result[cluster_id] = {"pod_cidr": pod_cidr, "service_cidr": service_cidr}

        return result
