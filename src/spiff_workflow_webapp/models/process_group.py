"""Process_group."""
from flask_bpmn.models.db import db


class ProcessGroupModel(db.Model):  # type: ignore
    """ProcessGroupMode."""

    __tablename__ = "process_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
