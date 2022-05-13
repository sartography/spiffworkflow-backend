"""User."""
from ..extensions import db


class User(db.Model):
    """User."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
