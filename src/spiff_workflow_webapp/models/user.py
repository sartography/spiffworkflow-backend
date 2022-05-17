"""User."""
from flask_bpmn.models.db import db
from sqlalchemy.orm import relationship


class UserModel(db.Model):
    """UserModel."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    user_group_assignments = relationship(
        "UserGroupAssignmentModel", cascade="all, delete"
    )
    groups = relationship("GroupModel", secondary="user_group_assignment")
