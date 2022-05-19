"""__init__.py."""
import os
from werkzeug.utils import ImportStringError

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def setup_config(app):
    """Setup_config."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.from_object("spiff_workflow_webapp.config.default")

    try:
        app.config.from_object("spiff_workflow_webapp.config." + app.env)
    except ImportStringError as exception:
        raise Exception(
            "Cannot find config file for FLASK_ENV: " + app.env
        ) from exception
