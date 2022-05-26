"""Data_store."""
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from sqlalchemy import func

from flask_bpmn.models.db import db


class DataStoreModel(db.Model):
    """DataStoreModel."""

    __tablename__ = "data_store"
    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now())
    key = db.Column(db.String, nullable=False)
    workflow_id = db.Column(db.Integer)
    task_spec = db.Column(db.String)
    spec_id = db.Column(db.String)
    user_id = db.Column(db.String, nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=True)
    value = db.Column(db.String)


class DataStoreSchema(SQLAlchemyAutoSchema):
    """DataStoreSchema."""

    class Meta:
        """Meta."""

        model = DataStoreModel
        load_instance = True
        include_fk = True
        sqla_session = db.session
