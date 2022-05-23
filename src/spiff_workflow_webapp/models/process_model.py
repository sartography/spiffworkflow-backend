"""Process_model."""
from flask_bpmn.models.db import db
from sqlalchemy import ForeignKey  # type: ignore

from spiff_workflow_webapp.models.process_group import ProcessGroupModel


class ProcessModel(db.Model):  # type: ignore
    """ProcessModel."""

    __tablename__ = "process_model"
    id = db.Column(db.Integer, primary_key=True)
    process_group_id = db.Column(ForeignKey(ProcessGroupModel.id), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.String(50))
