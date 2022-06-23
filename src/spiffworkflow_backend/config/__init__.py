"""__init__.py."""
import logging
import os

from flask.app import Flask
from werkzeug.utils import ImportStringError


def setup_logger_for_sql_statements(app: Flask) -> None:
    """Setup_logger_for_sql_statements."""
    db_log_file_name = f"log/db_{app.env}.log"
    db_handler_log_level = logging.INFO
    db_logger_log_level = logging.DEBUG
    db_handler = logging.FileHandler(db_log_file_name)
    db_handler.setLevel(db_handler_log_level)
    db_logger = logging.getLogger("sqlalchemy")
    db_logger.propagate = False
    db_logger.addHandler(db_handler)
    db_logger.setLevel(db_logger_log_level)


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

    setup_database_uri(app)
    setup_logger_for_sql_statements(app)

    env_config_module = "spiffworkflow_backend.config." + app.env
    try:
        app.config.from_object(env_config_module)
    except ImportStringError as exception:
        raise ModuleNotFoundError(
            f"Cannot find config module: {env_config_module}"
        ) from exception
