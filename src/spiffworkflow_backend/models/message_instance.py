"""Message_instance."""
import enum
from dataclasses import dataclass
from typing import Any

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import validates

from spiffworkflow_backend.models.message_model import MessageModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel


class MessageTypes(enum.Enum):
    """MessageTypes."""

    send = "send"
    receive = "receive"


@dataclass
class MessageInstanceModel(SpiffworkflowBaseDBModel):
    """Messages from a process instance that are ready to send to a receiving task."""

    __tablename__ = "queued_send_message"

    id = db.Column(db.Integer, primary_key=True)
    process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=False)  # type: ignore
    bpmn_element_id = db.Column(db.String(50), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)
    message_model_id = db.Column(ForeignKey(MessageModel.id), nullable=False)

    @validates("message_type")
    def validate_message_type(self, _key: str, value: Any) -> Any:
        """Validate_message_type."""
        try:
            m_type = getattr(MessageTypes, value, None)
        except Exception as e:
            raise ValueError(f"invalid message type: {value}") from e

        if m_type:
            return m_type.value

        return None
