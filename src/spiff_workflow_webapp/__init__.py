"""__init__."""
from flask import Flask
from flask_bpmn.models.db import db
from flask_bpmn.models.db import migrate

from spiff_workflow_webapp.routes.api import api
from spiff_workflow_webapp.routes.user_blueprint import user_blueprint
import flask.app


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
    app.register_blueprint(api)

    return app
