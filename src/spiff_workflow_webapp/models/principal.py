"""Principal."""
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user import UserModel


class PrincipalModel(db.Model):  # type: ignore
    """PrincipalModel."""

    __tablename__ = "principal"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    group_id = db.Column(ForeignKey(GroupModel.id), nullable=False)
