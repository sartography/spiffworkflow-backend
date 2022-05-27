"""APIs for dealing with process groups, process models, and process instances."""

import connexion
from flask import Blueprint, g, render_template

admin_blueprint = Blueprint("admin", __name__, template_folder='templates', static_folder='static')

@admin_blueprint.route("/index", methods=["GET"])
def hello_world():
    return render_template('index.html')
