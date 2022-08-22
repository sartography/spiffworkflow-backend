"""Message_correlation_property."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel


class MessageCorrelationPropertyModel(SpiffworkflowBaseDBModel):
    """MessageCorrelationPropertyModel."""

    __tablename__ = "message_correlation_property"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), index=True, unique=True)
    updated_at_in_seconds: int = db.Column(db.Integer)
    created_at_in_seconds: int = db.Column(db.Integer)
