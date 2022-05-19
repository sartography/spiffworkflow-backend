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

    # NOTE: set this here since nox shoves tests and src code to
    # different places and this allows us to know exactly where we are at the start
    app.config["BPMN_SPEC_ABSOLUTE_DIR"] = (
        os.path.join(os.path.dirname(__file__))
        + "/tests/spiff_workflow_webapp/files/bpmn_specs"
    )

    return app
