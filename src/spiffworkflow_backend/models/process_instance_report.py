"""Process_instance."""

from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.user import UserModel


class ProcessInstanceReportModel(db.Model):  # type: ignore
    """ProcessInstanceReportModel."""

    __tablename__ = "process_instance_report"
    id = db.Column(db.Integer, primary_key=True)
    process_model_identifier = db.Column(db.String(50), nullable=False, index=True)
    process_group_identifier = db.Column(db.String(50), nullable=False, index=True)
    report_json = deferred(db.Column(db.JSON))
    created_by_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    created_by = relationship("UserModel")
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    @property
    def serialized(self):
        """Return object data in serializeable format."""
        return {
            "id": self.id,
            "process_model_identifier": self.process_model_identifier,
            "process_group_identifier": self.process_group_identifier,
            "report_json": self.report_json,
            "created_by": self.process_initiator_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
