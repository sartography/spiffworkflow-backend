"""Conftest."""
import pytest

from spiff_workflow_webapp import create_app
from flask.app import Flask


@pytest.fixture(scope="session")
def app() -> Flask:
    """App."""
    app = create_app()
    return app
