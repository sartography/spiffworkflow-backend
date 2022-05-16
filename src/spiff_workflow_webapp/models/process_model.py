from flask_bpmn.models.db import db
from sqlalchemy.orm import deferred


class ProcessModel(db.Model):
    __tablename__ = 'process_models'
    id = db.Column(db.Integer, primary_key=True)
    bpmn_json = deferred(db.Column(db.JSON))
