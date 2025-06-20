"""Main Flask app entrypoint."""

from __future__ import annotations

import os
import subprocess

import yaml
from flasgger import Swagger
from flask import Flask

from smo.config import configs
from smo.flask import error_handlers
from smo.models import db
from smo.flask.routes.cluster.cluster import cluster
from smo.flask.routes.hdag.graph import graph
from smo.flask.routes.nfvcl.os_k8s import os_k8s
from smo.flask.routes.nfvcl.vim import vim

env = os.environ.get("FLASK_ENV", "development")

ROOT_PATH = os.path.dirname(__file__)

ERROR_HANDLERS = [
    (subprocess.CalledProcessError, error_handlers.handle_subprocess_error),
    (yaml.YAMLError, error_handlers.handle_yaml_read_error),
]


def create_app(app_name="smo", config=None):
    """Function that returns a configured Flask app."""

    app = Flask(app_name, root_path=ROOT_PATH)
    app.config.from_object(configs[env])

    # Override with any additional config passed
    if config:
        for key, value in config.items():
            app.config[key] = value

    setup_swagger(app)

    register_blueprints(app)
    register_error_handlers(app)

    setup_db(app)

    return app


def register_blueprints(app):
    app.register_blueprint(cluster)
    app.register_blueprint(graph)
    app.register_blueprint(os_k8s)
    app.register_blueprint(vim)


def register_error_handlers(app):
    for exception, handler in ERROR_HANDLERS:
        app.register_error_handler(exception, handler)


def setup_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # TODO / FIXME !!!!
        # fetch_clusters(
        #     app.config["KARMADA_KUBECONFIG"],
        #     app.config["SUBMARINER_KUBECONFIG"],
        #     app.config["GRAFANA_HOST"],
        #     app.config["GRAFANA_USERNAME"],
        #     app.config["GRAFANA_PASSWORD"],
        # )


def setup_swagger(app):
    app.config["SWAGGER"] = {
        "title": "SMO-API",
        "uiversion": 3,
        "specs_route": "/docs/",
        "specs": [
            {
                "endpoint": "smo-api-spec",
                "route": "/smo-api-spec.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "ui_params": {
            "apisSorter": "alpha",
            "operationsSorter": "alpha",
            "tagsSorter": "alpha",
        },
        "ui_params_text": (
            "{\n"
            '    "operationsSorter": (a, b) => {\n'
            '        var order = { "get": "0", "post": "1", "put": "2", "delete": "3" };\n'
            '        return order[a.get("method")].localeCompare(order[b.get("method")]);\n'
            "    }\n"
            "}"
        ),
    }
    Swagger(app=app)


if __name__ == "__main__":
    app = create_app()
    app.run()
