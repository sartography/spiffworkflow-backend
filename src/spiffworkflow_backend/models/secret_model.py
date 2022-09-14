"""Secret_model."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from marshmallow import Schema
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.user import UserModel


class SecretModel(SpiffworkflowBaseDBModel):
    """SecretModel."""

    __tablename__ = "secret"
    id: int = db.Column(db.Integer, primary_key=True)
    key: str = db.Column(db.String(50))
    value: str = db.Column(db.Text())
    creator_user_id: int = db.Column(ForeignKey(UserModel.id), nullable=False)

    allowed_processes = relationship("SecretAllowedProcessPathModel", cascade="delete")


class SecretModelSchema(Schema):
    """SecretModelSchema."""

    class Meta:
        """Meta."""

        model = SecretModel
        fields = ["key", "value", "creator_user_id"]


class SecretAllowedProcessPathModel(SpiffworkflowBaseDBModel):
    """Allowed processes can be Process Groups or Process Models.

    We store the path in either case.
    """

    __tablename__ = "secret_allowed_process"
    id: int = db.Column(db.Integer, primary_key=True)
    secret_id: int = db.Column(ForeignKey(SecretModel.id), nullable=False)  # type: ignore
    allowed_relative_path: str = db.Column(db.String(500), nullable=False, index=True)
