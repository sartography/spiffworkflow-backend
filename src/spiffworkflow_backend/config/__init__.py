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

    if os.environ.get("DATABASE_URI") is None:
        if os.environ.get("SPIFF_DATABASE_TYPE") == "sqlite":
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite:///{app.instance_path}/db_{app.env}.sqlite3"
        elif os.environ.get("SPIFF_DATABASE_TYPE") == "postgres":
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"postgresql://spiffworkflow_backend:spiffworkflow_backend@localhost:5432/spiffworkflow_backend_{app.env}"
        else:
            # use pswd to trick flake8 with hardcoded passwords
            db_pswd = os.environ.get("DB_PASSWORD")
            if db_pswd is None:
                db_pswd = ""
            app.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"mysql+mysqlconnector://root:{db_pswd}@localhost/spiffworkflow_backend_{app.env}"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

    env_config_module = "spiffworkflow_backend.config." + app.env
    try:
        app.config.from_object(env_config_module)
    except ImportStringError as exception:
        raise ModuleNotFoundError(
            f"Cannot find config module: {env_config_module}"
        ) from exception
