"""Bare-metal Kubernetes cluster endpoints."""

from flasgger import swag_from
from flask import Blueprint, current_app

from services.nfvcl.bm_k8s_service import fetch_clusters

bm_k8s = Blueprint('bm_k8s', __name__, url_prefix='/bm_k8s')


@bm_k8s.route('/clusters', methods=['GET'])
@swag_from('swagger/bm_k8s/get_bm_clusters.yaml')
def get_bm_clusters():
    """Fetches all Bare-metal Kubernetes clusters."""

    nfvcl_base_url = current_app.config['NFVCL_BASE_URL']
    return fetch_clusters(nfvcl_base_url), 200
