from unittest.mock import patch

from utils.prometheus_helper import PrometheusHelper


@patch('utils.prometheus_helper.requests.get')
def test_prometheus_helper_get_latency(mock_get):
    """Test PrometheusHelper get_latency method."""
    mock_get.return_value.json.return_value = {'data': {'result': [{'value': [0, '0.5']}]}}
    helper = PrometheusHelper('http://mock-prometheus')
    assert helper.get_latency('test-service') == 0.5


@patch('utils.prometheus_helper.requests.get')
def test_prometheus_helper_get_request_rate(mock_get):
    """Test PrometheusHelper get_request_rate method."""
    mock_get.return_value.json.return_value = {'data': {'result': [{'value': [0, '10']}]}}
    helper = PrometheusHelper('http://mock-prometheus')
    assert helper.get_request_rate('test-service') == 10.0
