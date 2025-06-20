"""Application graph service node table."""

from models import db
from sqlalchemy import JSON


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(255))
    grafana = db.Column(db.String(255))
    cluster_affinity = db.Column(db.String(255))
    artifact_ref = db.Column(db.String(255))
    artifact_type = db.Column(db.String(255))
    artifact_implementer = db.Column(db.String(255))
    cpu = db.Column(db.String(255))
    memory = db.Column(db.String(255))
    storage = db.Column(db.String(255))
    gpu = db.Column(db.String(255))
    values_overwrite = db.Column(JSON)
    alert = db.Column(JSON)

    graph = db.relationship("Graph", back_populates="services")
    graph_id = db.Column(db.Integer, db.ForeignKey("graph.id"), nullable=False)

    def to_dict(self):
        """Returns a dictionary representation of the class."""

        instance_dict = {
            "name": self.name,
            "status": self.status,
            "grafana": self.grafana,
            "cluster_affinity": self.cluster_affinity,
            "cpu": self.cpu,
            "memory": self.memory,
            "storage": self.storage,
            "gpu": self.gpu,
            "values_overwrite": self.values_overwrite,
            "artifact_ref": self.artifact_ref,
            "artifact_type": self.artifact_type,
            "artifact_implementer": self.artifact_implementer,
        }

        return instance_dict
