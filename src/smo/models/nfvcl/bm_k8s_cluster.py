"""Bare-metal Kubernetes cluster."""

from __future__ import annotations

import random
import string

from sqlalchemy import event

from smo.models import db


class BM_K8S_cluster(db.Model):
    __tablename__ = "bm_k8s_clusters"

    smo_id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Event listener for generating unique ID for BM_K8S_cluster
@event.listens_for(BM_K8S_cluster, "before_insert")
def generate_bm_k8s_unique_id(mapper, connection, target):
    random_string = "".join(random.choices(string.ascii_letters, k=5))
    target.smo_id = f"BM_K8S_{target.pop_area}_{random_string}"
