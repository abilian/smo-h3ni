"""DB models declaration."""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from smo.models.cluster.cluster import Cluster
from smo.models.hdag.graph import Graph
from smo.models.hdag.service import Service
from smo.models.nfvcl.bm_k8s_cluster import BM_K8S_cluster
from smo.models.nfvcl.os_k8s_cluster import OS_K8S_cluster
from smo.models.nfvcl.vim import VIM
