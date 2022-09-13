"""Spiff_logging."""
from dataclasses import dataclass
from typing import Optional

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel


@dataclass
class SpiffLoggingModel(SpiffworkflowBaseDBModel):
    """LoggingModel."""

    __tablename__ = "spiff_logging"
    id: int = db.Column(db.Integer, primary_key=True)
    process_instance_id: int = db.Column(
        db.Integer, nullable=False
    )  # record.process_instance_id
    bpmn_process_identifier: str = db.Column(
        db.String(50), nullable=False
    )  # record.workflow
    task: str = db.Column(db.String(50), nullable=False)  # record.task_id
    timestamp: float = db.Column(db.Float(), nullable=False)  # record.created

    message: Optional[str] = db.Column(db.String(50), nullable=True)  # record.msg
