"""Bare-metal Kubernetes cluster endpoints."""

from flasgger import swag_from
from flask import Blueprint, current_app

from services.cluster.cluster_service import fetch_clusters

cluster = Blueprint('cluster', __name__, url_prefix='/clusters')


@cluster.route('/', methods=['GET'])
@swag_from('swagger/get_clusters.yaml')
def get_clusters():
    """Fetches all Bare-metal Kubernetes clusters."""

    clusters = fetch_clusters(
        current_app.config['KARMADA_KUBECONFIG'],
        current_app.config['GRAFANA_HOST'], current_app.config['GRAFANA_USERNAME'], current_app.config['GRAFANA_PASSWORD']
    )
    return clusters, 200
