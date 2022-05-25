"""Process_instance."""

import enum
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy import Enum  # type: ignore
from sqlalchemy.orm import deferred  # type: ignore
from sqlalchemy.orm import relationship

from spiff_workflow_webapp.models.user import UserModel


class ProcessInstanceStatus(enum.Enum):
    not_started = "not_started"
    user_input_required = "user_input_required"
    waiting = "waiting"
    complete = "complete"
    erroring = "erroring"


class ProcessInstanceModel(db.Model):  # type: ignore
    """ProcessInstanceModel."""

    __tablename__ = "process_instance"
    id = db.Column(db.Integer, primary_key=True)
    process_model_identifier = db.Column(db.String, nullable=False)
    bpmn_json = deferred(db.Column(db.JSON))
    start_in_seconds = db.Column(db.Integer)
    end_in_seconds = db.Column(db.Integer)
    process_initiator_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    process_initiator = relationship("UserModel")
    status = db.Column(db.Enum(ProcessInstanceStatus))
