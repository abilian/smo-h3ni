"""Virtual Infrastructure Manager"""

from __future__ import annotations

from smo.models import db


class VIM(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pop_area = db.Column(db.Integer)
    vim_name = db.Column(db.String(50))
    vim_url = db.Column(db.String(100))
    vim_type = db.Column(db.String(50))
    vim_networks = db.Column(db.JSON)
    mgmt_network = db.Column(db.String(50))
    service_network = db.Column(db.String(50))
    use_floating_ip = db.Column(db.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


"""
Test POST a new SMO_VIM
{
  "pop_area": 3,
  "vim_name": "Test_vim",
  "vim_url": "test_url",
  "vim_type": "Openstack",
  "vim_networks": ["net1","net2"],
  "mgmt_network": "net1",
  "service_network": "net2",
  "use_floating_ip": true
}
"""
