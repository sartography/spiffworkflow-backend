"""PermissionTarget."""
import re
from typing import Any
from sqlalchemy.orm import validates
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel


class InvalidPermissionTargetUri(Exception):
    pass

class PermissionTargetModel(SpiffworkflowBaseDBModel):
    """PermissionTargetModel."""

    __tablename__ = "permission_target"

    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(255), unique=True, nullable=False)

    @validates("uri")
    def validate_uri(self, key: str, value: str) -> str:
        if re.search(r"%.", value):
            raise InvalidPermissionTargetUri(
                f"Invalid Permission Target Uri: {value}"
            )
        return value
