"""Message_correlation."""
from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.message_instance import MessageInstanceModel


@dataclass
class MessageCorrelationModel(SpiffworkflowBaseDBModel):
    """Message Correlations to relate queued messages together."""

    __tablename__ = "message_correlation"
    __table_args__ = (
        db.UniqueConstraint(
            "message_id", "name", name="message_id_name_unique"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(ForeignKey(MessageInstanceModel.id), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.String(50), nullable=False, index=True)
