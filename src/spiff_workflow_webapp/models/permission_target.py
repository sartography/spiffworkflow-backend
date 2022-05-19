"""PermissionTarget."""
from flask_bpmn.models.db import db
# from sqlalchemy import ForeignKey  # type: ignore
# from sqlalchemy.orm import relationship  # type: ignore

# from spiff_workflow_webapp.models.principal import PrincipalModel
# from spiff_workflow_webapp.models.permission import PermissionModel


class PermissionTargetModel(db.Model):  # type: ignore
    """PermissionTargetModel."""

    __tablename__ = "permission_target"
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    # group_id = db.Column(ForeignKey(GroupModel.id), nullable=False)
