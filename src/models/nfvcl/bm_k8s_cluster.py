"""Bare-metal Kubernetes cluster."""

import random
import string

from sqlalchemy import event

from models import db


class BM_K8S_cluster(db.Model):
    __tablename__ = 'bm_k8s_clusters'

    smo_id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    # deployment_type = db.Column(Enum('os', 'bm', name='deployment_type'), default='os')
    # vim_name = db.Column(db.String(100))
    is_master_area = db.Column(db.Boolean, default=True)
    # nfvcl_id = db.Column(db.String(50))
    pop_area = db.Column(db.Integer)
    master_flavor = db.Column(db.JSON)
    mgmt_network = db.Column(db.String(100))
    service_network = db.Column(db.String(100))
    running_workers = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Event listener for generating unique ID for BM_K8S_cluster
@event.listens_for(BM_K8S_cluster, 'before_insert')
def generate_bm_k8s_unique_id(mapper, connection, target):
    random_string = ''.join(random.choices(string.ascii_letters, k=5))
    target.smo_id = f"BM_K8S_{target.pop_area}_{random_string}"
