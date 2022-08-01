"""Message_instance."""
import enum

from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import Enum
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.message_model import MessageModel


class MessageTypes(enum.Enum):
    """MessageTypes."""
    send = 1
    receive = 2


@dataclass
class MessageInstanceModel(SpiffworkflowBaseDBModel):
    """Messages from a process instance that are ready to send to a receiving task."""

    __tablename__ = "queued_send_message"

    id = db.Column(db.Integer, primary_key=True)
    process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=False)  # type: ignore
    bpmn_element_id = db.Column(db.String(50), nullable=False)
    messsage_type = db.Column(Enum(MessageTypes), nullable=False)
    message_model = db.Column(ForeignKey(MessageModel.id), nullable=False)
