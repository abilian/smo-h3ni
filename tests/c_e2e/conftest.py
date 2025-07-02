import pytest
from unittest.mock import patch

from flask import Flask
from flask.testing import FlaskClient

from smo.flask.app import create_app
from smo.utils.helpers import format_memory

CONFIG = {
    "FLASK_ENV": "development",
    "KARMADA_KUBECONFIG": "test-kube.config",
    "GRAFANA_HOST": "http://mock-grafana",
    "GRAFANA_USERNAME": "admin",
    "GRAFANA_PASSWORD": "admin_pass",
    "INSECURE_REGISTRY": "True",
    "PROMETHEUS_HOST": "http://mock-prometheus",
    "SCALING_ENABLED": "False",
    "SCALING_INTERVAL": "30",
    "NFVCL_BASE_URL": "http://mock-nfvcl",
    #
    # "DB_HOST": "localhost",
    # "DB_PORT": "65432",
    # "DB_NAME": "smo",
    # "DB_USER": "smo_user",
    # "DB_PASSWORD": "smo_pass",
    "SQLALCHEMY_DATABASE_URI": "postgresql://smo_user:smo_pass@localhost:65432/smo",
}


class TestPrometheusHelper:
    """Mock class for PrometheusHelper to simulate Prometheus interactions in tests."""

    def __init__(self, prometheus_host, time_window="30", time_unit="s"):
        self.prometheus_host = prometheus_host
        self.time_window = time_window
        self.time_unit = time_unit

    def get_request_rate(self, name):
        return 10.0

    def update_alert_rules(self, alert, action):
        pass


class TestGrafanaHelper:
    """Mock class for GrafanaHelper to simulate Grafana interactions in tests."""

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
    """Mock class for KarmadaHelper to simulate Karmada interactions in tests."""

    def __init__(self, config_file_path, namespace="default"):
        self.config_file_path = config_file_path
        self.namespace = namespace
        self.deployments = {
            "test-deployment-1": {
                "desired_replicas": 3,
                "current_replicas": 3,
                "cpu_limit": 2.0,
            }
        }

    def get_cluster_info(self):
        return {
            "test-cluster-1": {
                "total_cpu": 16.0,
                "allocated_cpu": 4.0,
                "remaining_cpu": 12.0,
                "total_memory_bytes": format_memory(64 * 1024**3),
                "allocated_memory_bytes": format_memory(16 * 1024**3),
                "remaining_memory_bytes": format_memory(48 * 1024**3),
                "availability": True,
            },
            "test-cluster-2": {
                "total_cpu": 32.0,
                "allocated_cpu": 10.0,
                "remaining_cpu": 22.0,
                "total_memory_bytes": format_memory(128 * 1024**3),
                "allocated_memory_bytes": format_memory(30 * 1024**3),
                "remaining_memory_bytes": format_memory(98 * 1024**3),
                "availability": False,
            },
        }

    def get_desired_replicas(self, name):
        return self.deployments.get(name, {}).get("desired_replicas", 1)

    def get_replicas(self, name):
        return self.deployments.get(name, {}).get("current_replicas", 1)

    def get_cpu_limit(self, name):
        return self.deployments.get(name, {}).get("cpu_limit", 1.0)

    def scale_deployment(self, name, replicas):
        if name in self.deployments:
            self.deployments[name]["desired_replicas"] = replicas
            self.deployments[name]["current_replicas"] = replicas


@pytest.fixture
def app():
    """Fixture to create a Flask app with custom environment variables for testing."""

    with (
        patch("smo.utils.grafana_helper.GrafanaHelper", TestGrafanaHelper),
        patch("smo.utils.karmada_helper.KarmadaHelper", TestKarmadaHelper),
        patch("smo.utils.prometheus_helper.PrometheusHelper", TestPrometheusHelper),
    ):
        # from smo.app import create_app
        app = create_app(config=CONFIG)
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Fixture to create a test client for the Flask app."""

    return app.test_client()
