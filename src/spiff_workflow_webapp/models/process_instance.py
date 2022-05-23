"""Process_instance."""
from flask_bpmn.models.db import db
from sqlalchemy.orm import deferred  # type: ignore
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy.orm import relationship

from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.models.process_model import ProcessModel


class ProcessInstanceModel(db.Model):  # type: ignore
    """ProcessInstanceModel."""

    __tablename__ = "process_instance"
    id = db.Column(db.Integer, primary_key=True)
    process_model_id = db.Column(ForeignKey(ProcessModel.id), nullable=False)
    bpmn_json = deferred(db.Column(db.JSON))
    start_in_seconds = db.Column(db.Integer)
    end_in_seconds = db.Column(db.Integer)
    process_initiator_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    process_initiator = relationship("UserModel")
