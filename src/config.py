"""Flask app configurations."""

import os

from dotenv import load_dotenv

load_dotenv()

SWAGGER_CONFIG = {
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


def str_to_bool(str_variable):
    return str_variable.lower() in ('t', 'true')


class Config:
    """Database connection credentials."""
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/{}'.format(
        os.getenv('DB_USER', 'root'),
        os.getenv('DB_PASSWORD', 'password'),
        os.getenv('DB_HOST', 'localhost'),
        os.getenv('DB_NAME', 'smo')
    )
    KARMADA_KUBECONFIG = '/home/python/.kube/{}'.format(
        os.getenv('KARMADA_KUBECONFIG', 'karmada-apiserver.config')
    )
    NFVCL_BASE_URL = os.getenv('NFVCL_BASE_URL')
    INSECURE_REGISTRY = str_to_bool(os.getenv('INSECURE_REGISTRY', 'True'))
    PROMETHEUS_HOST = os.getenv('PROMETHEUS_HOST')
    SCALING_INTERVAL = os.getenv('SCALING_INTERVAL')
    GRAFANA_HOST = os.getenv('GRAFANA_HOST')
    GRAFANA_USERNAME = os.getenv('GRAFANA_USERNAME')
    GRAFANA_PASSWORD = os.getenv('GRAFANA_PASSWORD')
    SCALING_ENABLED = str_to_bool(os.getenv('SCALING_ENABLED'))
    SWAGGER = SWAGGER_CONFIG


class ProdConfig(Config):
    """Production settings."""
    FLASK_ENV = 'production'
    DEBUG = False


class DevConfig(Config):
    """Development settings."""
    FLASK_ENV = 'development'
    DEBUG = True


configs = {
    'default': ProdConfig,
    'production': ProdConfig,
    'development': DevConfig,
}
