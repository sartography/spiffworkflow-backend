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
    app.config.from_object("spiffworkflow_backend.config.default")

    if os.environ.get("SPIFF_DATABASE_TYPE") == "sqlite":
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
        ] = f"mysql+mysqlconnector://root:{mysql_pswd}@localhost/spiffworkflow_backend_{app.env}"

    env_config_module = "spiffworkflow_backend.config." + app.env
    try:
        app.config.from_object(env_config_module)
    except ImportStringError as exception:
        raise ModuleNotFoundError(
            f"Cannot find config module: {env_config_module}"
        ) from exception
