from unittest.mock import patch, MagicMock

from utils.karmada_helper import KarmadaHelper


@patch('utils.karmada_helper.client.AppsV1Api.read_namespaced_deployment')
def test_karmada_helper_get_replicas(mock_read_deployment):
    """Test KarmadaHelper get_replicas method."""

    mock_read_deployment.return_value.status.available_replicas = 3
    helper = KarmadaHelper('mock-config')
    assert helper.get_replicas('test-deployment') == 3


@patch('utils.karmada_helper.client.AppsV1Api.read_namespaced_deployment')
def test_karmada_helper_get_cpu_limit(mock_read_deployment):
    """Test KarmadaHelper get_cpu_limit method."""

    mock_read_deployment.return_value.spec.template.spec.containers[0].resources.limits = {'cpu': '500m'}
    helper = KarmadaHelper('mock-config')
    assert helper.get_cpu_limit('test-deployment') == 0.5
