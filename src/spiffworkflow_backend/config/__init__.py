"""__init__.py."""
import os
import threading

from flask.app import Flask
from werkzeug.utils import ImportStringError

from spiffworkflow_backend.services.logging_service import setup_logger


def setup_database_uri(app: Flask) -> None:
    """Setup_database_uri."""
    if os.environ.get("SPIFFWORKFLOW_BACKEND_DATABASE_URI") is None:
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
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SPIFFWORKFLOW_BACKEND_DATABASE_URI"
        )


def setup_config(app: Flask) -> None:
    """Setup_config."""
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.from_object("spiffworkflow_backend.config.default")
    # This allows config/testing.py or instance/config.py to override the default config
    if "ENV" in app.config and app.config["ENV"] == "testing":
        app.config.from_pyfile("config/testing.py", silent=True)
    else:
        app.config.from_pyfile(f"{app.instance_path}/config.py", silent=True)

    setup_database_uri(app)
    setup_logger(app)

    env_config_module = "spiffworkflow_backend.config." + app.env
    try:
        app.config.from_object(env_config_module)
    except ImportStringError as exception:
        raise ModuleNotFoundError(
            f"Cannot find config module: {env_config_module}"
        ) from exception

    thread_local_data = threading.local()
    app.config['THREAD_LOCAL_DATA'] = thread_local_data
