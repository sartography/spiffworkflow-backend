"""Conftest."""
import os
import shutil
from typing import Iterator

import pytest
from flask.app import Flask

from spiffworkflow_backend.services.process_model_service import ProcessModelService


# We need to call this before importing spiffworkflow_backend
# otherwise typeguard cannot work. hence the noqa: E402
if os.environ.get("RUN_TYPEGUARD") == "true":
    from typeguard.importhook import install_import_hook

    install_import_hook(packages="spiffworkflow_backend")


from spiffworkflow_backend import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app() -> Flask:
    """App."""
    os.environ["FLASK_ENV"] = "testing"
    # os.environ["FLASK_SESSION_SECRET_KEY"] = "this_is_testing_secret_key"
    os.environ["FLASK_SESSION_SECRET_KEY"] = "super_secret_key"
    app = create_app()

    # NOTE: set this here since nox shoves tests and src code to
    # different places and this allows us to know exactly where we are at the start
    app.config["BPMN_SPEC_ABSOLUTE_DIR"] = (
        os.path.join(os.path.dirname(__file__))
        + "/tests/spiffworkflow_backend/files/bpmn_specs"
    )

    return app


@pytest.fixture()
def with_bpmn_file_cleanup() -> Iterator[None]:
    """Process_group_resource."""
    try:
        yield
    finally:
        process_model_service = ProcessModelService()
        if os.path.exists(process_model_service.root_path()):
            shutil.rmtree(process_model_service.root_path())
