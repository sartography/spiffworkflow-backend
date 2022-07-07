"""PermissionAssignment."""
import enum
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel

from sqlalchemy import Enum
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.permission_target import PermissionTargetModel
from spiffworkflow_backend.models.principal import PrincipalModel


class GrantDeny(enum.Enum):
    """GrantDeny."""

    grant = 1
    deny = 2


class Permission(enum.Enum):
    """Permission."""

    instantiate = 1
    administer = 2
    view_instance = 3


class PermissionAssignmentModel(SpiffworkflowBaseDBModel):
    """PermissionAssignmentModel."""

    __tablename__ = "permission_assignment"
    id = db.Column(db.Integer, primary_key=True)
    principal_id = db.Column(ForeignKey(PrincipalModel.id), nullable=False)
    permission_target_id = db.Column(
        ForeignKey(PermissionTargetModel.id), nullable=False
    )
    grant_type = db.Column(Enum(GrantDeny))
    permission = db.Column(Enum(Permission))
