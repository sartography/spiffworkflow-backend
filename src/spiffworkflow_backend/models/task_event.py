"""Task_event."""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from marshmallow import fields
from marshmallow import INCLUDE
from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import func


if TYPE_CHECKING:
    from spiffworkflow_backend.models.process_instance import ProcessInstanceModel  # noqa: F401


class TaskAction(enum.Enum):
    """TaskAction."""

    COMPLETE = "COMPLETE"
    TOKEN_RESET = "TOKEN_RESET"  # noqa: S105
    HARD_RESET = "HARD_RESET"
    SOFT_RESET = "SOFT_RESET"
    ASSIGNMENT = "ASSIGNMENT"  # Whenever the lane changes between tasks we assign the task to specific user.


class TaskEventModel(SpiffworkflowBaseDBModel):
    """TaskEventModel."""

    __tablename__ = "task_event"
    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    user_uid = db.Column(  # type: ignore
        db.String(50), nullable=False  # type: ignore
    )  # In some cases the unique user id may not exist in the db yet.
    process_instance_id = db.Column(  # type: ignore
        db.Integer, db.ForeignKey("process_instance.id"), nullable=False  # type: ignore
    )
    spec_version = db.Column(db.String(50))  # type: ignore
    action = db.Column(db.String(50))  # type: ignore
    task_id = db.Column(db.String(50))  # type: ignore
    task_name = db.Column(db.String(50))  # type: ignore
    task_title = db.Column(db.String(50))  # type: ignore
    task_type = db.Column(db.String(50))  # type: ignore
    task_state = db.Column(db.String(50))  # type: ignore
    task_lane = db.Column(db.String(50))  # type: ignore
    form_data = db.Column(  # type: ignore
        db.JSON  # type: ignore
    )  # And form data submitted when the task was completed.
    mi_type = db.Column(db.String(50))  # type: ignore
    mi_count = db.Column(db.Integer)  # type: ignore
    mi_index = db.Column(db.Integer)  # type: ignore
    process_name = db.Column(db.String(50))  # type: ignore
    date = db.Column(db.DateTime(timezone=True), default=func.now())  # type: ignore


class TaskEventModelSchema(SQLAlchemyAutoSchema):
    """TaskEventModelSchema."""

    class Meta:
        """Meta."""

        model = TaskEventModel
        load_instance = True
        include_relationships = True
        include_fk = True  # Includes foreign keys


class TaskEvent:
    """TaskEvent."""

    def __init__(self, model: TaskEventModel, process_instance: "ProcessInstanceModel"):
        """__init__."""
        self.id = model.id
        self.process_instance = process_instance
        self.user_uid = model.user_uid
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

    process_instance = fields.Nested("ProcessInstanceMetadataSchema", dump_only=True)
    task_lane = fields.String(allow_none=True, required=False)

    class Meta:
        """Meta."""

        model = TaskEvent
        additional = [
            "id",
            "user_uid",
            "action",
            "task_id",
            "task_title",
            "task_name",
            "task_type",
            "task_state",
            "task_lane",
            "date",
        ]
        unknown = INCLUDE
