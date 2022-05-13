"""Main."""
from flask import Blueprint

from ..extensions import db
from ..models.user import User

main = Blueprint("main", __name__)


@main.route("/user/<name>")
def create_user(name):
    """Create_user."""
    user = User(name=name)
    db.session.add(user)
    db.session.commit()

    return "Created User!"
