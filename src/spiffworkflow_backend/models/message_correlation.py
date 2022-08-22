"""Message_correlation."""
from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.message_correlation_property import (
    MessageCorrelationPropertyModel,
)
from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel

# message_correlation
# process_instance_id: 4
# correlation_key (and properties): number
# value: 5

# message_instance_message_correlation:
# message_instance_id
# message_correlation_id

# message_instance:
# correlation_key (and properties): number


@dataclass
class MessageCorrelationModel(SpiffworkflowBaseDBModel):
    """Message Correlations to relate queued messages together."""

    __tablename__ = "message_correlation"
    __table_args__ = (
        db.UniqueConstraint(
            "process_instance_id",
            "message_correlation_property_id",
            "name",
            name="message_instance_id_name_unique",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    process_instance_id = db.Column(
        ForeignKey(ProcessInstanceModel.id), nullable=False, index=True  # type: ignore
    )
    message_correlation_property_id = db.Column(
        ForeignKey(MessageCorrelationPropertyModel.id), nullable=False, index=True
    )
    name = db.Column(db.String(255), nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False, index=True)
    updated_at_in_seconds: int = db.Column(db.Integer)
    created_at_in_seconds: int = db.Column(db.Integer)


@dataclass
class MessageCorrelationMessageInstanceModel(SpiffworkflowBaseDBModel):
    """MessageCorrelationMessageInstanceModel."""

    __tablename__ = "message_correlation_message_instance"

    __table_args__ = (
        db.UniqueConstraint(
            "message_instance_id",
            "message_correlation_id",
            name="message_correlation_message_instance_unique",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    message_instance_id = db.Column(
        ForeignKey(MessageInstanceModel.id), nullable=False, index=True
    )
    message_correlation_id = db.Column(
        ForeignKey(MessageCorrelationModel.id), nullable=False, index=True
    )
