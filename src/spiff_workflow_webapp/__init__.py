"""__init__."""
import flask.app
from flask import Flask
from flask_bpmn.api.api_error import api_error_blueprint
from flask_bpmn.models.db import db
from flask_bpmn.models.db import migrate

from spiff_workflow_webapp.routes.api_blueprint import api_blueprint
from spiff_workflow_webapp.routes.user_blueprint import user_blueprint


def create_app() -> flask.app.Flask:
    """Create_app."""
    app = Flask(__name__)
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+mysqlconnector://root:@localhost/spiff_workflow_webapp_development"
    # app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://crc_user:crc_pass@localhost:5432/spiff_test"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(api_error_blueprint)

    return app
