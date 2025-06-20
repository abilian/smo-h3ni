"""Bare-metal Kubernetes cluster business logic."""

import requests
from werkzeug.exceptions import InternalServerError


def fetch_clusters(nfvcl_base_url):
    headers = {"accept": "application/json"}

    try:
        response = requests.get(
            f"{nfvcl_base_url}/nfvcl/v2/api/blue/?detailed=false", headers=headers
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
        blue_data = response.json()

        return "To be done!"

    except requests.exceptions.RequestException as e:
        raise InternalServerError(str(e))
