"""Active_task."""
from __future__ import annotations

from dataclasses import dataclass

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey

from spiffworkflow_backend.models.principal import PrincipalModel


@dataclass
class ActiveTaskModel(SpiffworkflowBaseDBModel):
    """ActiveTaskModel."""

    __tablename__ = "active_task"
    __table_args__ = (
        db.UniqueConstraint(
            "task_id", "process_instance_id", name="active_task_unique"
        ),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    task_id: str = db.Column(db.String(50), nullable=False)
    process_instance_id: int = db.Column(db.Integer, nullable=False)
    assigned_principal_id: int = db.Column(ForeignKey(PrincipalModel.id))
    process_instance_data: str = db.Column(db.Text)
    status: str = db.Column(db.String(50), nullable=False)

    updated_at_in_seconds: int = db.Column(db.Integer)
    created_at_in_seconds: int = db.Column(db.Integer)
