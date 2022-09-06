"""Spiff_logging."""

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel


# @dataclass
class SpiffLoggingModel(SpiffworkflowBaseDBModel):
    """LoggingModel."""

    __tablename__ = "spiff_logging"
    id: int = db.Column(db.Integer, primary_key=True)
    process: int = db.Column(db.Integer)
    task: str = db.Column(db.String(50))
    status: str = db.Column(db.String(50))
