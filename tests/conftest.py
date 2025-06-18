import pytest
from unittest.mock import patch
from pytest import MonkeyPatch

from utils.helpers import format_memory


class TestGrafanaHelper:
    def __init__(self, *args, **kwargs):
        pass

    def publish_dashboard(self, dashboard_json):
        return {"url": "http:://mock-grafana/d/test-dashboard/test-dashboard"}

    def create_cluster_dashboard(self, cluster_name):
        return {}

    def create_graph_dashboard(self, graph_name, service_names):
        return {}

    def create_graph_service(self, service_name):
        return {}


class TestKarmadaHelper:
    def __init__(self, config_file_path, namespace='default'):
        self.config_file_path = config_file_path
        self.namespace = namespace
        self.deployments = {
            'test-deployment-1': {
                'desired_replicas': 3,
                'current_replicas': 3,
                'cpu_limit': 2.0
            }
        }

    def get_cluster_info(self):
        return {
            'test-cluster-1': {
                'total_cpu': 16.0,
                'allocated_cpu': 4.0,
                'remaining_cpu': 12.0,
                'total_memory_bytes': format_memory(64 * 1024**3),
                'allocated_memory_bytes': format_memory(16 * 1024**3),
                'remaining_memory_bytes': format_memory(48 * 1024**3),
                'availability': True,
            },
            'test-cluster-2': {
                'total_cpu': 32.0,
                'allocated_cpu': 10.0,
                'remaining_cpu': 22.0,
                'total_memory_bytes': format_memory(128 * 1024**3),
                'allocated_memory_bytes': format_memory(30 * 1024**3),
                'remaining_memory_bytes': format_memory(98 * 1024**3),
                'availability': False,
            }
        }

    def get_desired_replicas(self, name):
        return self.deployments.get(name, {}).get('desired_replicas', 1)

    def get_replicas(self, name):
        return self.deployments.get(name, {}).get('current_replicas', 1)

    def get_cpu_limit(self, name):
        return self.deployments.get(name, {}).get('cpu_limit', 1.0)

    def scale_deployment(self, name, replicas):
        if name in self.deployments:
            self.deployments[name]['desired_replicas'] = replicas
            self.deployments[name]['current_replicas'] = replicas


@pytest.fixture
def custom_env_app():
    with MonkeyPatch.context() as mp:
        mp.setenv('FLASK_ENV', 'development')
        mp.setenv('KARMADA_KUBECONFIG', 'test-kube.config')
        mp.setenv('GRAFANA_HOST', 'http://mock-grafana')
        mp.setenv('GRAFANA_USERNAME', 'admin')
        mp.setenv('GRAFANA_PASSWORD', 'admin_pass')
        mp.setenv('INSECURE_REGISTRY', 'True')
        mp.setenv('SCALING_ENABLED', 'False')
        mp.setenv('PROMETHEUS_HOST', 'http://mock-prometheus')
        mp.setenv('SCALING_INTERVAL', '30')
        mp.setenv('NFVCL_BASE_URL', 'http://mock-nfvcl')
        mp.setenv('DB_USER', 'test_user')
        mp.setenv('DB_PASSWORD', 'test_pass')
        mp.setenv('DB_HOST', 'localhost')
        mp.setenv('DB_NAME', 'smo_test')
        mp.setenv('DB_PORT', '5432')

        with patch('utils.grafana_helper.GrafanaHelper', TestGrafanaHelper):
            with patch('utils.karmada_helper.KarmadaHelper', TestKarmadaHelper):
                from app import create_app
                app = create_app()
                yield app


@pytest.fixture
def client(custom_env_app):
    return custom_env_app.test_client()
