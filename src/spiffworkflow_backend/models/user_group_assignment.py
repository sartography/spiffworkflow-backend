"""UserGroupAssignment."""
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore


class UserGroupAssignmentModel(db.Model):  # type: ignore
    """UserGroupAssignmentModel."""

    __tablename__ = "user_group_assignment"
    __table_args__ = (
        db.UniqueConstraint("user_id", "group_id", name="user_group_assignment_unique"),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey("user.id"), nullable=False)
    group_id = db.Column(ForeignKey("group.id"), nullable=False)
    group = relationship("GroupModel", overlaps="groups,user_group_assignments,users")
    user = relationship("UserModel", overlaps="groups,user_group_assignments,users")