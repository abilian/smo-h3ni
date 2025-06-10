"""Cluster table."""

from models import db


class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    available_cpu = db.Column(db.Float, nullable=False)
    available_ram = db.Column(db.String, nullable=False)
    availability = db.Column(db.Boolean, nullable=False)
    acceleration = db.Column(db.Boolean, nullable=False)
    grafana = db.Column(db.String)


    def to_dict(self):
        """Returns a dictionary representation of the class."""

        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'available_cpu': self.available_cpu,
            'available_ram': self.available_ram,
            'availability': self.availability,
            'acceleration': self.acceleration,
            'grafana': self.grafana
        }
