"""Openstack Kubernetes cluster."""

from __future__ import annotations

import random
import string

from sqlalchemy import event

from smo.models import db


class OS_K8S_cluster(db.Model):
    __tablename__ = "os_k8s_clusters"

    smo_id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    # deployment_type = db.Column(Enum('os', 'bm', name='deployment_type'), default='os')
    # vim_name = db.Column(db.String(100))
    is_master_area = db.Column(db.Boolean, default=True)  # NFVCL Blueprint key
    nfvcl_id = db.Column(db.String(50))  # NFVCL id
    pop_area = db.Column(db.Integer)
    master_flavor = db.Column(db.JSON)
    mgmt_network = db.Column(db.String(100))
    service_network = db.Column(db.String(100))
    running_workers = db.Column(db.Integer)
    karmada_details = db.Column(db.JSON)  # Something about Karmada
    submariner_details = db.Column(db.JSON)  # Something about Submariner

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Define event listener function to generate unique ID
@event.listens_for(OS_K8S_cluster, "before_insert")
def generate_unique_id(mapper, connection, target):
    random_string = "".join(random.choices(string.ascii_letters, k=5))
    target.smo_id = f"OS_K8S_{target.pop_area}_{random_string}"
