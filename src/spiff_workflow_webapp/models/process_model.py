"""Process_model."""
from flask_bpmn.models.db import db
from sqlalchemy.orm import deferred  # type: ignore


class ProcessModel(db.Model):  # type: ignore
    """ProcessModel."""

    __tablename__ = "process_model"
    id = db.Column(db.Integer, primary_key=True)
    bpmn_json = deferred(db.Column(db.JSON))
