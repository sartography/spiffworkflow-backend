"""User."""
from flask_bpmn.models.db import db
from sqlalchemy.orm import relationship  # type: ignore


class UserModel(db.Model):  # type: ignore
    """UserModel."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    user_group_assignments = relationship("UserGroupAssignmentModel", cascade="delete")
    groups = relationship(
        "GroupModel",
        viewonly=True,
        secondary="user_group_assignment",
        overlaps="user_group_assignments,users",
    )
