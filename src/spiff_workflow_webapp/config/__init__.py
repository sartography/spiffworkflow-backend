"""__init__.py."""
import os

from flask.app import Flask
from werkzeug.utils import ImportStringError


def setup_config(app: Flask) -> None:
    """Setup_config."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.from_object("spiff_workflow_webapp.config.default")
    app.config["PROJECT_ROOT"] = os.path.join(app.root_path, "..", "..")

    try:
        app.config.from_object("spiff_workflow_webapp.config." + app.env)
    except ImportStringError as exception:
        raise Exception(
            "Cannot find config file for FLASK_ENV: " + app.env
        ) from exception
