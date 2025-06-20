import requests
from requests.auth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest

from utils.grafana_template import (
    create_basic_dashboard,
    create_dashboard_variables,
    create_panels_cluster,
    create_panels_service,
)


class GrafanaHelper:
    def __init__(self, grafana_host, username="admin", password="prom-operator"):
        self.grafana_host = grafana_host
        self.auth = HTTPBasicAuth(username, password)

    def publish_dashboard(self, dashboard_json):
        """Pushes the specified Grafana dashboard."""

        url = f"{self.grafana_host}/api/dashboards/db"
        res = requests.post(url, json=dashboard_json, auth=self.auth)
        if res.status_code != 200:
            raise BadRequest(res.json())
        return res.json()

    def create_cluster_dashboard(self, cluster_name):
        dashboard = create_basic_dashboard(cluster_name)
        dashboard["dashboard"]["panels"] = create_panels_cluster(cluster_name)
        return dashboard

    def create_graph_dashboard(self, graph_name, service_names):
        dashboard = create_basic_dashboard(graph_name)
        templated_service_name = "service"
        dashboard["dashboard"]["panels"] = create_panels_service(
            f"${templated_service_name}"
        )
        dashboard["dashboard"]["templating"] = create_dashboard_variables(
            templated_service_name, service_names
        )
        return dashboard

    def create_graph_service(self, service_name):
        dashboard = create_basic_dashboard(service_name)
        dashboard["dashboard"]["panels"] = create_panels_service(service_name)
        return dashboard
