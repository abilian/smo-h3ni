from devtools import debug
from py_pglite.sqlalchemy import SQLAlchemyPGliteManager

from smo.app import create_app


def test_app():
    with SQLAlchemyPGliteManager() as manager:
        engine = manager.get_engine()
        url = engine.url

        debug(url)

        # Extract connection details for any PostgreSQL client
        host = url.host or "localhost"
        port = url.port or 5432
        database = url.database

        db_uri = f"postgresql+psycopg://{host}:{port}/{database}"

        app = create_app(
            config={
                "SQLALCHEMY_DATABASE_URI": db_uri,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        )
        assert app is not None
