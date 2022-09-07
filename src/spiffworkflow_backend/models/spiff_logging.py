"""Spiff_logging."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from marshmallow import Schema


class SpiffLoggingModel(SpiffworkflowBaseDBModel):
    """LoggingModel."""

    __tablename__ = "spiff_logging"
    id: int = db.Column(db.Integer, primary_key=True)
    process_instance_id: int = db.Column(db.Integer)  # record.process_instance_id
    process_id: str = db.Column(db.String(50))  # record.workflow
    task: str = db.Column(db.String(50))  # record.task_id
    message: str = db.Column(db.String(50))  # record.msg
    timestamp: float = db.Column(db.Float())  # record.created


class SpiffLoggingModelSchema(Schema):
    """SpiffLoggingModelSchema."""

    class Meta:
        """Meta."""

        model = SpiffLoggingModel
        fields = ["process_instance_id", "process_id", "task", "message", "timestamp"]
