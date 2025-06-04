"""Main Flask app entrypoint."""

import os
import subprocess

import yaml
from flask import Flask
from flasgger import Swagger

from config import configs
from errors import error_handlers
from models import db
from routes.hdag.graph import graph
from routes.cluster.cluster import cluster
from routes.nfvcl.os_k8s import os_k8s
from routes.nfvcl.vim import vim
from services.cluster.cluster_service import fetch_clusters

env = os.environ.get('FLASK_ENV', 'development')

ROOT_PATH = os.path.dirname(__file__)


def create_app(app_name='smo'):
    """Function that returns a configured Flask app."""

    app = Flask(app_name, root_path=ROOT_PATH)

    app.config['SWAGGER'] = {
        'title': 'SMO-API',
        'uiversion': 3,
        'specs_route': '/docs/',
        'specs': [
            {
                'endpoint': 'smo-api-spec',
                'route': '/smo-api-spec.json',
                'rule_filter': lambda rule: True,  # all in
                'model_filter': lambda tag: True,  # all in
            }
        ],
        'ui_params': {
            'apisSorter': 'alpha',
            'operationsSorter': 'alpha',
            'tagsSorter': 'alpha'
        },
        'ui_params_text': (
            '{\n'
            '    "operationsSorter": (a, b) => {\n'
            '        var order = { "get": "0", "post": "1", "put": "2", "delete": "3" };\n'
            '        return order[a.get("method")].localeCompare(order[b.get("method")]);\n'
            '    }\n'
            '}'
        )
    }
    Swagger(app=app)

    app.config.from_object(configs[env])

    app.register_blueprint(cluster)
    app.register_blueprint(graph)
    app.register_blueprint(os_k8s)
    app.register_blueprint(vim)

    app.register_error_handler(
        subprocess.CalledProcessError,
        error_handlers.handle_subprocess_error
    )
    app.register_error_handler(
        yaml.YAMLError,
        error_handlers.handle_yaml_read_error
    )

    db.init_app(app)
    with app.app_context():
        db.create_all()
        fetch_clusters(
            app.config['KARMADA_KUBECONFIG'],
            app.config['SUBMARINER_KUBECONFIG'],
            app.config['GRAFANA_HOST'],
            app.config['GRAFANA_USERNAME'],
            app.config['GRAFANA_PASSWORD'],
        )

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
