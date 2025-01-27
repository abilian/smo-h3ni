"""Bare-metal Kubernetes cluster endpoints."""

from flasgger import swag_from
from flask import Blueprint, current_app

from services.cluster.cluster_service import fetch_clusters

cluster = Blueprint('cluster', __name__, url_prefix='/clusters')


@cluster.route('/', methods=['GET'])
@swag_from('swagger/get_clusters.yaml')
def get_clusters():
    """Fetches all Bare-metal Kubernetes clusters."""

    return fetch_clusters(current_app.config['KARMADA_KUBECONFIG']), 200
