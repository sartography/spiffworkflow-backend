"""Active_data"""

from dataclasses import dataclass
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel

@dataclass
class ActiveDataModel(SpiffworkflowBaseDBModel):
    __tablename__ = "active_data"

    id = db.Column(db.Integer, primary_key=True)
    spiffworkflow_task_data: str = db.Column(db.Text)