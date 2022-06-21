"""Data_store."""
from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from flask_marshmallow.sqla import SQLAlchemyAutoSchema  # type: ignore


class DataStoreModel(SpiffworkflowBaseDBModel):
    """DataStoreModel."""

    __tablename__ = "data_store"
    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    updated_at_in_seconds = db.Column(db.Integer)  # type: ignore
    key = db.Column(db.String(50), nullable=False)  # type: ignore
    process_instance_id = db.Column(db.Integer)  # type: ignore
    task_spec = db.Column(db.String(50))  # type: ignore
    spec_id = db.Column(db.String(50))  # type: ignore
    user_id = db.Column(db.String(50), nullable=True)  # type: ignore
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=True)  # type: ignore
    value = db.Column(db.String(50))  # type: ignore


class DataStoreSchema(SQLAlchemyAutoSchema):  # type: ignore
    """DataStoreSchema."""

    class Meta:
        """Meta."""

        model = DataStoreModel
        load_instance = True
        include_fk = True
        sqla_session = db.session
