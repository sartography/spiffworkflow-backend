"""PermissionAssignment."""
import enum
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy import Enum

from spiff_workflow_webapp.models.principal import PrincipalModel
from spiff_workflow_webapp.models.permission import PermissionModel
from spiff_workflow_webapp.models.permission_target import PermissionTargetModel


class GrantDeny(enum.Enum):
    """GrantDeny."""
    grant = 1
    deny = 2


class PermissionAssignmentModel(db.Model):  # type: ignore
    """PermissionAssignmentModel."""

    __tablename__ = "permission_assignment"
    id = db.Column(db.Integer, primary_key=True)
    principal_id = db.Column(ForeignKey(PrincipalModel.id), nullable=False)
    permission_id = db.Column(ForeignKey(PermissionModel.id), nullable=False)
    permission_target_id = db.Column(ForeignKey(PermissionTargetModel.id), nullable=False)
    grant_type = db.Column(Enum(GrantDeny))
