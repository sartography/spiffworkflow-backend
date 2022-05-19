"""Permission."""
from flask_bpmn.models.db import db


class PermissionModel(db.Model):  # type: ignore
    """PermissionModel."""

    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
