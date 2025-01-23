"""Kubernetes cluster business logic."""

from models import db, Cluster
from utils.karmada_helper import KarmadaHelper


def fetch_clusters(karmada_kubeconfig):
    """Retrieves all cluster data."""

    cluster_dict = []

    karmada_helper = KarmadaHelper(karmada_kubeconfig)
    cluster_info = karmada_helper.get_cluster_info()

    for cluster_name, info in cluster_info.items():
        cluster = db.session.query(Cluster).filter(Cluster.name == cluster_name).first()
        if cluster is not None:
            cluster.available_cpu = info['remaining_cpu']
            cluster.available_ram = info['remaining_memory_bytes']
        else:
            cluster = Cluster(
                name=cluster_name,
                location='Unknown',
                available_cpu=info['remaining_cpu'],
                available_ram=info['remaining_memory_bytes'],
                availability=info['availability'],
                acceleration=0,
                grafana='N/A'
            )
            db.session.add(cluster)
        db.session.commit()

        cluster_dict.append(cluster.to_dict())

    return cluster_dict
