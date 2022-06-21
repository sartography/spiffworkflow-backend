"""UserGroupAssignment."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class UserGroupAssignmentModel(SpiffworkflowBaseDBModel):  # type: ignore
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
