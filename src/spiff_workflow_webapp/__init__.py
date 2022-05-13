from flask import Flask

from .routes.api import api
from .routes.main import main
from spiff_workflow_webapp.extensions import db
from spiff_workflow_webapp.extensions import migrate


def create_app():
    """Create_app."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)
    app.register_blueprint(api)

    return app
