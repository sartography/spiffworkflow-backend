"""UserGroupAssignment."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class UserGroupAssignmentModel(SpiffworkflowBaseDBModel):
    """UserGroupAssignmentModel."""

    __tablename__ = "user_group_assignment"
    __table_args__ = (
        db.UniqueConstraint("user_id", "group_id", name="user_group_assignment_unique"),  # type: ignore
    )
    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    user_id = db.Column(ForeignKey("user.id"), nullable=False)  # type: ignore
    group_id = db.Column(ForeignKey("group.id"), nullable=False)  # type: ignore
    group = relationship("GroupModel", overlaps="groups,user_group_assignments,users")  # type: ignore
    user = relationship("UserModel", overlaps="groups,user_group_assignments,users")  # type: ignore
