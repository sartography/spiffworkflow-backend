"""UserGroupAssignment."""
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user import UserModel


class UserGroupAssignmentModel(db.Model):
    """UserGroupAssignmentModel."""

    __tablename__ = "user_group_assignment"
    __table_args__ = (
        db.UniqueConstraint('user_id', 'group_id', name='user_group_assignment_unique'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    group_id = db.Column(ForeignKey(GroupModel.id), nullable=False)
    group = relationship("GroupModel")
    user = relationship("UserModel")
