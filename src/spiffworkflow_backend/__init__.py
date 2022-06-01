"""__init__."""
import os

import connexion
import flask.app
from flask_bpmn.api.api_error import api_error_blueprint
from flask_bpmn.models.db import db
from flask_bpmn.models.db import migrate

from spiffworkflow_backend.config import setup_config
from spiffworkflow_backend.routes.admin_blueprint.admin_blueprint import admin_blueprint
from spiffworkflow_backend.routes.api_blueprint import api_blueprint
from spiffworkflow_backend.routes.process_api_blueprint import process_api_blueprint
from spiffworkflow_backend.routes.user_blueprint import user_blueprint


def create_app() -> flask.app.Flask:
    """Create_app."""
    # We need to create the sqlite database in a known location.
    # If we rely on the app.instance_path without setting an environment
    # variable, it will be one thing when we run flask db upgrade in the
    # noxfile and another thing when the tests actually run.
    # instance_path is described more at https://flask.palletsprojects.com/en/2.1.x/config/
    connexion_app = connexion.FlaskApp(
        __name__, server_args={"instance_path": os.environ.get("FLASK_INSTANCE_PATH")}
    )
    app = connexion_app.app
    app.config["CONNEXION_APP"] = connexion_app
    app.config["SESSION_TYPE"] = "filesystem"

    if os.environ.get("FLASK_SESSION_SECRET_KEY") is None:
        raise KeyError("Cannot find the secret_key from the environment. Please set FLASK_SESSION_SECRET_KEY")

    app.secret_key = os.environ.get("FLASK_SESSION_SECRET_KEY")

    setup_config(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(process_api_blueprint)
    app.register_blueprint(api_error_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    connexion_app.add_api("api.yml", base_path="/v1.0")

    return app
