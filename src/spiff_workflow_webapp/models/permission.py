"""Permission."""
from flask_bpmn.models.db import db
from sqlalchemy.orm import relationship  # type: ignore


class PermissionModel(db.Model):  # type: ignore
    """PermissionModel."""

    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    # user_group_assignments = relationship("UserGroupAssignmentModel", cascade="delete")
    # groups = relationship(
    #     "GroupModel",
    #     viewonly=True,
    #     secondary="user_group_assignment",
    #     overlaps="user_group_assignments,users",
    # )
