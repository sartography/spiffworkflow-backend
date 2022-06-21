"""PermissionTarget."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel

from sqlalchemy.schema import CheckConstraint

# from sqlalchemy import ForeignKey  # type: ignore

# from spiffworkflow_backend.models.process_group import ProcessGroupModel
# from spiffworkflow_backend.models.process_model import ProcessModel


class PermissionTargetModel(SpiffworkflowBaseDBModel):  # type: ignore
    """PermissionTargetModel."""

    __tablename__ = "permission_target"
    __table_args__ = (
        CheckConstraint(
            "NOT(process_group_id IS NULL AND process_model_identifier IS NULL AND process_instance_id IS NULL)"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    # process_group_id = db.Column(ForeignKey(ProcessGroupModel.id), nullable=True)
    # process_model_identifier = db.Column(ForeignKey(ProcessModel.id), nullable=True)
    # process_instance_id = db.Column(ForeignKey(ProcessInstanceModel.id), nullable=True)
