"""Flask app configurations."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def str_to_bool(str_variable: str | None, default: bool | None = None) -> bool:  # noqa: FBT001
    if str_variable is None:
        if default is not None:
            return default
        raise ValueError("str_variable cannot be None and no default provided")
    return str_variable.lower() in {"t", "true"}


class Config:
    """Database connection credentials."""
    #
    # if "FLASK_SQLALCHEMY_DATABASE_URI" in os.environ:
    #     SQLALCHEMY_DATABASE_URI = os.environ["FLASK_SQLALCHEMY_DATABASE_URI"]
    # else:
    #     SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:5432/{}".format(
    #         os.getenv("DB_USER", "root"),
    #         os.getenv("DB_PASSWORD", "password"),
    #         os.getenv("DB_HOST", "localhost"),
    #         os.getenv("DB_NAME", "smo"),
    #     )
    # KARMADA_KUBECONFIG = f"/home/python/.kube/{os.getenv('KARMADA_KUBECONFIG', 'karmada-apiserver.config')}"
    # SUBMARINER_KUBECONFIG = (
    #     f"/home/python/.kube/{os.getenv('SUBMARINER_KUBECONFIG', 'config')}"
    # )
    # NFVCL_BASE_URL = os.getenv("NFVCL_BASE_URL")
    # INSECURE_REGISTRY = str_to_bool(os.getenv("INSECURE_REGISTRY"), default=False)
    # PROMETHEUS_HOST = os.getenv("PROMETHEUS_HOST")
    # SCALING_INTERVAL = os.getenv("SCALING_INTERVAL")
    # GRAFANA_HOST = os.getenv("GRAFANA_HOST")
    # GRAFANA_USERNAME = os.getenv("GRAFANA_USERNAME")
    # GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD")
    # SCALING_ENABLED = str_to_bool(os.getenv("SCALING_ENABLED"), default=False)


class ProdConfig(Config):
    """Production settings."""

    FLASK_ENV = "production"
    DEBUG = False


class DevConfig(Config):
    """Development settings."""

    FLASK_ENV = "development"
    DEBUG = True


configs = {
    "default": ProdConfig,
    "production": ProdConfig,
    "development": DevConfig,
}
