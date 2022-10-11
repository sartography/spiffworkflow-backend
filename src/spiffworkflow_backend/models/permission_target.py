"""PermissionTarget."""
import re
from typing import Any
from sqlalchemy.orm import validates
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel

# process groups and models are not in the db
# from sqlalchemy import ForeignKey  # type: ignore
#
# from spiffworkflow_backend.models.process_group import ProcessGroupModel
# from spiffworkflow_backend.models.process_model import ProcessModel


class InvalidPermissionTargetUri(Exception):
    pass

class PermissionTargetModel(SpiffworkflowBaseDBModel):
    """PermissionTargetModel."""

    __tablename__ = "permission_target"
    # __table_args__ = (
    #     CheckConstraint(
    #         "NOT(process_group_id IS NULL AND process_model_identifier IS NULL AND process_instance_id IS NULL)"
    #     ),
    # )

    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(255), unique=True, nullable=False)
    # process_group_id = db.Column(ForeignKey(ProcessGroupModel.id), nullable=True)  # type: ignore
    # process_model_identifier = db.Column(ForeignKey(ProcessModel.id), nullable=True)  # type: ignore
    # process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=True)  # type: ignore

    @validates("uri")
    def validate_uri(self, key: str, value: str) -> str:
        if re.search(r"\*.", value):
            raise InvalidPermissionTargetUri(
                f"Invalid Permission Target Uri: {value}"
            )
        return value
