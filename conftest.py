"""Conftest."""
import pytest
from flask.app import Flask

from spiff_workflow_webapp import create_app


@pytest.fixture(scope="session")
def app() -> Flask:
    """App."""
    app = create_app()
    return app
