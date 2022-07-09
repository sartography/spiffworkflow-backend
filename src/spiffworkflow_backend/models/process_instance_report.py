"""Process_instance."""
from __future__ import annotations

from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_model_service import ProcessModelService


@dataclass
class ProcessInstanceReportModel(SpiffworkflowBaseDBModel):
    """ProcessInstanceReportModel."""

    __tablename__ = "process_instance_report"
    id = db.Column(db.Integer, primary_key=True)
    identifier: str = db.Column(db.String(50), nullable=False, index=True)
    process_model_identifier: str = db.Column(db.String(50), nullable=False, index=True)
    process_group_identifier = db.Column(db.String(50), nullable=False, index=True)
    report_metadata: dict = deferred(db.Column(db.JSON))  # type: ignore
    created_by_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    created_by = relationship("UserModel")
    created_at_in_seconds = db.Column(db.Integer)
    updated_at_in_seconds = db.Column(db.Integer)

    # @property
    # def serialized(self) -> dict[str, Union[str, int]]:
    #     """Return object data in serializeable format."""
    #     return {
    #         "id": self.id,
    #         "process_model_identifier": self.process_model_identifier,
    #         "process_group_identifier": self.process_group_identifier,
    #         "report_metadata": self.report_metadata,
    #         "created_by": self.process_initiator_id,
    #         "created_at_in_seconds": self.created_at_in_seconds,
    #         "updated_at_in_seconds": self.updated_at_in_seconds,
    #     }

    @classmethod
    def add_fixtures(cls) -> None:
        """Add_fixtures."""
        try:
            process_model = ProcessModelService().get_process_model(
                group_id="sartography-admin", process_model_id="ticket"
            )
            json = {"order": "month asc"}
            user = UserModel.query.first()
            process_instance_report = cls(
                identifier="for-month",
                process_group_identifier=process_model.process_group_id,
                process_model_identifier=process_model.id,
                created_by_id=user.id,
                report_metadata=json,
            )
            db.session.add(process_instance_report)
            db.session.commit()

        except ProcessEntityNotFoundError:
            print("NOPE")
            print("NOPE")
            print("NOPE")
            print("NOPE")

    @classmethod
    def create_with_attributes(
        cls,
        identifier: str,
        process_group_identifier: str,
        process_model_identifier: str,
        report_metadata: dict,
        user: UserModel,
    ) -> ProcessInstanceReportModel:
        """Create_with_attributes."""
        process_model = ProcessModelService().get_process_model(
            group_id=process_group_identifier, process_model_id=process_model_identifier
        )
        process_instance_report = cls(
            identifier=identifier,
            process_group_identifier=process_model.process_group_id,
            process_model_identifier=process_model.id,
            created_by_id=user.id,
            report_metadata=report_metadata,
        )
        db.session.add(process_instance_report)
        db.session.commit()
        return process_instance_report
