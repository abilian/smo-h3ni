"""Karmada helper class and utility functions."""


from kubernetes import client, config
from utils.helpers import format_memory, memory_to_bytes


class KarmadaHelper():
    """Karmada helper class."""

    def __init__(self, config_file_path, namespace='default'):
        self.namespace = namespace
        self.config_file_path = config_file_path

        config.load_kube_config(config_file=self.config_file_path)

        self.custom_api = client.AppsV1Api()


    def calculate_resources(self):
        group = "cluster.karmada.io"
        version = "v1alpha1"
        plural = "clusters"

        clusters = self.custom_api.list_cluster_custom_object(group, version, plural)

        for cluster in clusters['items']:
            allocatable = cluster['status']['resourceSummary']['allocatable']
            allocated = cluster['status']['resourceSummary']['allocated']

            total_cpu = int(allocatable['cpu'])
            allocated_cpu = int(allocated['cpu'])

            total_memory = memory_to_bytes(allocatable['memory'])
            allocated_memory = memory_to_bytes(allocated['memory'])

            remaining_cpu = total_cpu - allocated_cpu
            remaining_memory = total_memory - allocated_memory

        return {
            "total_cpu": total_cpu,
            "allocated_cpu": allocated_cpu,
            "remaining_cpu": remaining_cpu,
            "total_memory_bytes": total_memory,
            "allocated_memory_bytes": allocated_memory,
            "remaining_memory_bytes": format_memory(remaining_memory),
        }
