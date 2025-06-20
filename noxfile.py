from __future__ import annotations

import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=PYTHON_VERSIONS[0], venv_backend="uv")
def lint(session: nox.Session):
    install_env(session)
    session.run("ruff", "check", *session.posargs)


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def pytest(session: nox.Session):
    install_env(session)
    session.run("pytest", *session.posargs)


# Based on https://nox.thea.codes/en/stable/cookbook.html#using-a-lockfile
def install_env(session: nox.Session):
    session.run_install(
        "uv",
        "sync",
        "--frozen",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
