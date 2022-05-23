"""Principal."""
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy.schema import CheckConstraint  # type: ignore

from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user import UserModel


class PrincipalModel(db.Model):  # type: ignore
    """PrincipalModel."""

    __tablename__ = "principal"
    __table_args__ = (CheckConstraint("NOT(user_id IS NULL AND group_id IS NULL)"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey(UserModel.id), nullable=True)
    group_id = db.Column(ForeignKey(GroupModel.id), nullable=True)
