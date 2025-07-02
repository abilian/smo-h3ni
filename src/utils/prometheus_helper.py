import math

import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class PrometheusHelper():
    """Helper class to execute Prometheus queries."""

    def __init__(self, prometheus_host, time_window='5', time_unit='s'):
        self.prometheus_host = prometheus_host
        self.time_window = time_window
        self.time_unit = time_unit


    def get_request_rate(self, name):
        """Returns the request completion rate of the service."""

        prometheus_request_rate_metric_name = 'sum(rate(flask_http_request_total{{service="{0}"}}'\
            '[{1}{2}]))by(service)'.format(name, self.time_window, self.time_unit)

        # Get arrival rate
        request_rate = self.query_prometheus(
            self.prometheus_host,
            prometheus_request_rate_metric_name
        )
        if math.isnan(request_rate):
            request_rate = 0.0
        return request_rate


    def query_prometheus(self, prometheus_host, query_name):
        """Helper function that fetches the desired metric from the prometheus endpoint."""

        prometheus_endpoint = f'{prometheus_host}/api/v1/query'
        response = requests.get(
            prometheus_endpoint,
            params={
                'query': query_name,
            },
            timeout=5
        )

        results = response.json()['data']['result']
        if len(results) > 0:
            return float(results[0]['value'][1])
        else:
            return float('NaN')


    def update_alert_rules(self, alert, action):
        """Update prometheus rules depending on action. Either `add` or `remove`"""

        name = 'kube-prometheus-stack-0'
        namespace = 'monitoring'
        group_name = 'smo-alerts'

        reload_url = f'{self.prometheus_host}/-/reload'
        try:
            # Load Kubernetes configuration
            config.load_kube_config()
            api_instance = client.CustomObjectsApi()

            # Fetch the existing PrometheusRule
            prometheus_rule = api_instance.get_namespaced_custom_object(
                group='monitoring.coreos.com',
                version='v1',
                namespace=namespace,
                plural='prometheusrules',
                name=name
            )

            for group in prometheus_rule['spec']['groups']:
                if group['name'] == group_name:
                    if action == 'add':
                        if 'rules' not in group:
                            group['rules'] = []
                        group['rules'].append(alert)
                    else:
                        new_rules = [rule for rule in group['rules'] if rule['alert'] != alert['alert']]
                        group['rules'] = new_rules
                else:
                    raise ValueError(f"Group '{group_name}' not found in the PrometheusRule.")

            # Update the PrometheusRule
            api_instance.replace_namespaced_custom_object(
                group='monitoring.coreos.com',
                version='v1',
                namespace=namespace,
                plural='prometheusrules',
                name=name,
                body=prometheus_rule
            )

            print('PrometheusRule updated successfully.')

            # Reload Prometheus
            response = requests.post(reload_url)
            if response.status_code != 200:
                print('Prometheus reloaded successfully.')
            else:
                print(f'Failed to reload Prometheus. Status code: {response.status_code}')

        except ApiException as e:
            print(f'Exception when updating PrometheusRule: {e}')
        except ValueError as ve:
            print(ve)
