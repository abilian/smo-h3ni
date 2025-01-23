"""Karmada helper class and utility functions."""


from kubernetes import client, config
from kubernetes.utils import parse_quantity

from utils.helpers import format_memory


class KarmadaHelper():
    """Karmada helper class."""

    def __init__(self, config_file_path, namespace='default'):
        self.namespace = namespace
        self.config_file_path = config_file_path

        config.load_kube_config(config_file=self.config_file_path)

        self.custom_api = client.CustomObjectsApi()


    def get_cluster_info(self):
        group = 'cluster.karmada.io'
        version = 'v1alpha1'
        plural = 'clusters'

        clusters = self.custom_api.list_cluster_custom_object(group, version, plural)

        result = {}
        for cluster in clusters['items']:
            cluster_name = cluster['metadata']['name']
            allocatable = cluster['status']['resourceSummary']['allocatable']
            allocated = cluster['status']['resourceSummary']['allocated']

            total_cpu = parse_quantity(allocatable['cpu'])
            allocated_cpu = parse_quantity(allocated['cpu'])

            total_memory = parse_quantity(allocatable['memory'])
            allocated_memory = parse_quantity(allocated['memory'])

            status = next((cond['status'] for cond in cluster['status']['conditions'] if cond['reason'] == 'ClusterReady'), None)
            availability = True if status == 'True' else False

            result[cluster_name] = {
                'total_cpu': float(total_cpu),
                'allocated_cpu': float(allocated_cpu),
                'remaining_cpu': float(total_cpu - allocated_cpu),
                'total_memory_bytes': format_memory(total_memory),
                'allocated_memory_bytes': format_memory(allocated_memory),
                'remaining_memory_bytes': format_memory(total_memory - allocated_memory),
                'availability': availability
            }

        return result
