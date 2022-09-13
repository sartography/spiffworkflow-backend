"""Secret_model."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.user import UserModel


class SecretModel(SpiffworkflowBaseDBModel):
    """SecretModel."""

    __tablename__ = "secret"
    id: int = db.Column(db.Integer, primary_key=True)
    service: str = db.Column(db.String(50))
    client: str = db.Column(db.String(50))
    key: str = db.Column(db.String(50))
    creator_user_id: int = db.Column(ForeignKey(UserModel.id), nullable=False)

    allowed_processes = relationship("SecretAllowedProcessPathModel", cascade="delete")  # type: ignore
    # allowed_processes: RelationshipProperty["SecretAllowedProcessPathModel"] = relationship(
    #     "SecretAllowedProcessPathModel"
    # )


class SecretAllowedProcessPathModel(SpiffworkflowBaseDBModel):
    """Allowed processes can be Process Groups or Process Models.

    We store the path in either case.
    """

    __tablename__ = "secret_allowed_process"
    id: int = db.Column(db.Integer, primary_key=True)
    secret_id: int = db.Column(ForeignKey(SecretModel.id), nullable=False)
    allowed_relative_path: str = db.Column(db.String(500), nullable=False, index=True)
