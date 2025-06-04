"""DB models declaration."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.cluster.cluster import Cluster
from models.hdag.graph import Graph
from models.hdag.service import Service
from models.nfvcl.bm_k8s_cluster import BM_K8S_cluster
from models.nfvcl.os_k8s_cluster import OS_K8S_cluster
from models.nfvcl.vim import VIM
