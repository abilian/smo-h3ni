from __future__ import annotations
import os

os.environ["FLASK_SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

from app import create_app

app = create_app()
assert app
