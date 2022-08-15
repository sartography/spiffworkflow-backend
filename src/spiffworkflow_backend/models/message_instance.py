"""Message_instance."""
import enum
from dataclasses import dataclass
from typing import Any
from typing import Optional

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import validates
from sqlalchemy.orm.events import event

from spiffworkflow_backend.models.message_model import MessageModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel


class MessageTypes(enum.Enum):
    """MessageTypes."""

    send = "send"
    receive = "receive"


class MessageStatuses(enum.Enum):
    """MessageStatuses."""

    ready = "ready"
    running = "running"
    completed = "completed"
    failed = "failed"


@dataclass
class MessageInstanceModel(SpiffworkflowBaseDBModel):
    """Messages from a process instance that are ready to send to a receiving task."""

    __tablename__ = "message_instance"

    id = db.Column(db.Integer, primary_key=True)
    process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=False)  # type: ignore
    message_model_id = db.Column(ForeignKey(MessageModel.id), nullable=False)

    bpmn_element_id = db.Column(db.String(50), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="ready")
    failure_cause = db.Column(db.String(255))

    def validate_enum_field(
        self, key: str, value: Any, enum_variable: enum.EnumMeta
    ) -> Any:
        """Validate_enum_field."""
        try:
            m_type = getattr(enum_variable, value, None)
        except Exception as e:
            raise ValueError(
                f"{self.__class__.__name__}: invalid {key}: {value}"
            ) from e

        if m_type is None:
            raise ValueError(f"{self.__class__.__name__}: invalid {key}: {value}")

        return m_type.value

    @validates("message_type")
    def validate_message_type(self, key: str, value: Any) -> Any:
        """Validate_message_type."""
        return self.validate_enum_field(key, value, MessageTypes)

    @validates("status")
    def validate_status(self, key: str, value: Any) -> Any:
        """Validate_status."""
        return self.validate_enum_field(key, value, MessageStatuses)


# This runs for ALL db flushes for ANY model, not just this one even if it's in the MessageInstanceModel class
# so this may not be worth it or there may be a better way to do it
#
# https://stackoverflow.com/questions/32555829/flask-validates-decorator-multiple-fields-simultaneously/33025472#33025472
# https://docs.sqlalchemy.org/en/14/orm/session_events.html#before-flush
@event.listens_for(Session, "before_flush")  # type: ignore
def validate_and_modify_relationships(
    session: Any, _flush_context: Optional[Any], _instances: Optional[Any]
) -> None:
    """Validate_and_modify_relationships."""
    for instance in session.new:
        if isinstance(instance, MessageInstanceModel):
            if instance.status == "failed" and instance.failure_cause is None:
                raise ValueError(
                    f"{instance.__class__.__name__}: failure_cause must be set if status is failed"
                )
