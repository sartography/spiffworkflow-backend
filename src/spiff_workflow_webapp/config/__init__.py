"""__init__.py."""
import os

from flask.app import Flask
from werkzeug.utils import ImportStringError


def setup_config(app: Flask) -> None:
    """Setup_config."""
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.from_object("spiff_workflow_webapp.config.default")

    if os.environ.get("TEST_DATABASE_TYPE") == "sqlite":
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"sqlite:///{app.instance_path}/db_{app.env}.sqlite3"
    else:
        # use pswd to trick flake8 with hardcoded passwords
        mysql_pswd = os.environ.get("MYSQL_PASSWORD")
        if mysql_pswd is None:
            mysql_pswd = ""
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"mysql+mysqlconnector://root:{mysql_pswd}@localhost/spiff_workflow_webapp_{app.env}"

    try:
        app.config.from_object("spiff_workflow_webapp.config." + app.env)
    except ImportStringError as exception:
        raise Exception(
            "Cannot find config file for FLASK_ENV: " + app.env
        ) from exception
