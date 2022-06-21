"""Group."""
from __future__ import annotations

from flask_bpmn.models.db import db
from flask_bpmn.models.group import FlaskBpmnGroupModel
from sqlalchemy.orm import relationship


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spiffworkflow_backend.models.user_group_assignment import UserGroupAssignmentModel
    from spiffworkflow_backend.models.user import UserModel


class GroupModel(FlaskBpmnGroupModel):
    """GroupModel."""

    __tablename__ = "group"
    __table_args__ = {"extend_existing": True}
    new_name_two = db.Column(db.String(255))  # type: ignore
    user_group_assignments = relationship(UserGroupAssignmentModel, cascade="delete")
    users = relationship(  # type: ignore
        UserModel,
        viewonly=True,
        secondary="user_group_assignment",
        overlaps="user_group_assignments,users",
    )
