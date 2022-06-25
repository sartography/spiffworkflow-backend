"""Process_instance."""
from typing import Union

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.user import UserModel


class ProcessInstanceReportModel(SpiffworkflowBaseDBModel):
    """ProcessInstanceReportModel."""

    __tablename__ = "process_instance_report"
    id = db.Column(db.Integer, primary_key=True)
    process_model_identifier = db.Column(db.String(50), nullable=False, index=True)
    process_group_identifier = db.Column(db.String(50), nullable=False, index=True)
    report_json = deferred(db.Column(db.JSON))  # type: ignore
    created_by_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    created_by = relationship("UserModel")
    created_at_in_seconds = db.Column(db.Integer)
    updated_at_in_seconds = db.Column(db.Integer)

    @property
    def serialized(self) -> dict[str, Union[str, int]]:
        """Return object data in serializeable format."""
        return {
            "id": self.id,
            "process_model_identifier": self.process_model_identifier,
            "process_group_identifier": self.process_group_identifier,
            "report_json": self.report_json,
            "created_by": self.process_initiator_id,
            "created_at_in_seconds": self.created_at_in_seconds,
            "updated_at_in_seconds": self.updated_at_in_seconds,
        }
