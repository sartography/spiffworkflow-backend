"""group."""
from flask_bpmn.models.db import db
from flask_bpmn.models.group import FlaskBpmnGroupModel
from sqlalchemy.orm import relationship


class GroupModel(FlaskBpmnGroupModel):
    """GroupModel."""

    __tablename__ = "group"
    __table_args__ = {"extend_existing": True}
    new_name_two = db.Column(db.String(255))
    user_group_assignments = relationship(
        "UserGroupAssignmentModel", cascade="delete"
    )
    users = relationship("UserModel", viewonly=True, secondary="user_group_assignment", overlaps="user_group_assignments,users")
