import pytest
from spiff_workflow_webapp import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app()
    return app
