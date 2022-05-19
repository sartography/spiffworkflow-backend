"""Conftest."""
import os

import pytest
from flask.app import Flask

from spiff_workflow_webapp import create_app


@pytest.fixture(scope="session")
def app() -> Flask:
    """App."""
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    return app
