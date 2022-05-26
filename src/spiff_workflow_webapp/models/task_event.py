"""Task_event."""
import enum

from marshmallow import INCLUDE, fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from flask_bpmn.models.db import db
from spiff_workflow_webapp.models.process_instance import ProcessInstanceMetadataSchema
from crc.models.workflow import WorkflowModel
from crc.services.ldap_service import LdapService
from sqlalchemy import func


class TaskAction(enum.Enum):
    """TaskAction."""
    COMPLETE = "COMPLETE"
    TOKEN_RESET = "TOKEN_RESET"
    HARD_RESET = "HARD_RESET"
    SOFT_RESET = "SOFT_RESET"
    ASSIGNMENT = "ASSIGNMENT"  # Whenever the lane changes between tasks we assign the task to specific user.


class TaskEventModel(db.Model):
    """TaskEventModel."""
    __tablename__ = 'task_event'
    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String, nullable=False)  # In some cases the unique user id may not exist in the db yet.
    process_instance_id = db.Column(db.Integer, db.ForeignKey('process_instance.id'), nullable=False)
    spec_version = db.Column(db.String)
    action = db.Column(db.String)
    task_id = db.Column(db.String)
    task_name = db.Column(db.String)
    task_title = db.Column(db.String)
    task_type = db.Column(db.String)
    task_state = db.Column(db.String)
    task_lane = db.Column(db.String)
    form_data = db.Column(db.JSON)  # And form data submitted when the task was completed.
    mi_type = db.Column(db.String)
    mi_count = db.Column(db.Integer)
    mi_index = db.Column(db.Integer)
    process_name = db.Column(db.String)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


class TaskEventModelSchema(SQLAlchemyAutoSchema):
    """TaskEventModelSchema."""
    class Meta:
        """Meta."""
        model = TaskEventModel
        load_instance = True
        include_relationships = True
        include_fk = True  # Includes foreign keys


class TaskEvent(object):
    """TaskEvent."""

    def __init__(self, model: TaskEventModel, process_instance: WorkflowModel):
        """__init__."""
        self.id = model.id
        self.process_instance = process_instance
        self.user_uid = model.user_uid
        self.user_display = LdapService.user_info(model.user_uid).display_name
        self.action = model.action
        self.task_id = model.task_id
        self.task_title = model.task_title
        self.task_name = model.task_name
        self.task_type = model.task_type
        self.task_state = model.task_state
        self.task_lane = model.task_lane
        self.date = model.date


class TaskEventSchema(Schema):
    """TaskEventSchema."""

    process_instance = fields.Nested(ProcessInstanceMetadataSchema, dump_only=True)
    task_lane = fields.String(allow_none=True, required=False)

    class Meta:
        """Meta."""
        model = TaskEvent
        additional = ["id", "user_uid", "user_display", "action", "task_id", "task_title",
                      "task_name", "task_type", "task_state", "task_lane", "date"]
        unknown = INCLUDE
