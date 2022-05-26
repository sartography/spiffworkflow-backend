"""User."""
from marshmallow import Schema
import marshmallow
from flask_bpmn.models.db import db
from sqlalchemy.orm import relationship  # type: ignore

from spiff_workflow_webapp.models.user_group_assignment import UserGroupAssignmentModel
from spiff_workflow_webapp.models.group import GroupModel


class UserModel(db.Model):  # type: ignore
    """UserModel."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    uid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    user_group_assignments = relationship("UserGroupAssignmentModel", cascade="delete")
    groups = relationship(
        "GroupModel",
        viewonly=True,
        secondary="user_group_assignment",
        overlaps="user_group_assignments,users",
    )


class UserModelSchema(Schema):
    """UserModelSchema."""
    class Meta:
        """Meta."""
        model = UserModel
        # load_instance = True
        # include_relationships = False
        # exclude = ("UserGroupAssignment",)
    id = marshmallow.fields.String(required=True)
    username = marshmallow.fields.String(required=True)


class AdminSessionModel(db.Model):
    __tablename__ = 'admin_session'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True)
    admin_impersonate_uid = db.Column(db.String(50))
