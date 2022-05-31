"""Process_instance."""
import enum

import marshmallow
from flask_bpmn.models.db import db
from marshmallow import INCLUDE
from marshmallow import Schema
from marshmallow_enum import EnumField
from SpiffWorkflow.navigation import NavItem
from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy import func
from sqlalchemy.orm import deferred  # type: ignore
from sqlalchemy.orm import relationship

from spiff_workflow_webapp.models.process_model import ProcessModelInfo
from spiff_workflow_webapp.models.task import TaskSchema
from spiff_workflow_webapp.models.user import UserModel


class NavigationItemSchema(Schema):
    """NavigationItemSchema."""

    class Meta:
        """Meta."""

        fields = [
            "spec_id",
            "name",
            "spec_type",
            "task_id",
            "description",
            "backtracks",
            "indent",
            "lane",
            "state",
            "children",
        ]
        unknown = INCLUDE

    state = marshmallow.fields.String(required=False, allow_none=True)
    description = marshmallow.fields.String(required=False, allow_none=True)
    backtracks = marshmallow.fields.String(required=False, allow_none=True)
    lane = marshmallow.fields.String(required=False, allow_none=True)
    task_id = marshmallow.fields.String(required=False, allow_none=True)
    children = marshmallow.fields.List(
        marshmallow.fields.Nested(lambda: NavigationItemSchema())
    )

    @marshmallow.post_load
    def make_nav(self, data, **kwargs):
        """Make_nav."""
        state = data.pop("state", None)
        task_id = data.pop("task_id", None)
        children = data.pop("children", [])
        spec_type = data.pop("spec_type", None)
        item = NavItem(**data)
        item.state = state
        item.task_id = task_id
        item.children = children
        item.spec_type = spec_type
        return item


class ProcessInstanceStatus(enum.Enum):
    """ProcessInstanceStatus."""

    not_started = "not_started"
    user_input_required = "user_input_required"
    waiting = "waiting"
    complete = "complete"
    erroring = "erroring"


class ProcessInstanceModel(db.Model):  # type: ignore
    """ProcessInstanceModel."""

    __tablename__ = "process_instance"
    id = db.Column(db.Integer, primary_key=True)
    process_model_identifier = db.Column(db.String(50), nullable=False, index=True)
    bpmn_json = deferred(db.Column(db.JSON))
    start_in_seconds = db.Column(db.Integer)
    end_in_seconds = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now())
    process_initiator_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    process_initiator = relationship("UserModel")
    status = db.Column(db.Enum(ProcessInstanceStatus))


class ProcessInstanceApi:
    """ProcessInstanceApi."""

    def __init__(
        self,
        id,
        status,
        next_task,
        process_model_identifier,
        total_tasks,
        completed_tasks,
        last_updated,
        is_review,
        title,
    ):
        """__init__."""
        self.id = id
        self.status = status
        self.next_task = next_task  # The next task that requires user input.
        #        self.navigation = navigation  fixme:  would be a hotness.
        self.process_model_identifier = process_model_identifier
        self.total_tasks = total_tasks
        self.completed_tasks = completed_tasks
        self.last_updated = last_updated
        self.title = title
        self.is_review = is_review


class ProcessInstanceApiSchema(Schema):
    """ProcessInstanceApiSchema."""

    class Meta:
        """Meta."""

        model = ProcessInstanceApi
        fields = [
            "id",
            "status",
            "next_task",
            "navigation",
            "process_model_identifier",
            "total_tasks",
            "completed_tasks",
            "last_updated",
            "is_review",
            "title",
            "study_id",
            "state",
        ]
        unknown = INCLUDE

    status = EnumField(ProcessInstanceStatus)
    next_task = marshmallow.fields.Nested(TaskSchema, dump_only=True, required=False)
    navigation = marshmallow.fields.List(
        marshmallow.fields.Nested(NavigationItemSchema, dump_only=True)
    )
    state = marshmallow.fields.String(allow_none=True)

    @marshmallow.post_load
    def make_process_instance(self, data, **kwargs):
        """Make_process_instance."""
        keys = [
            "id",
            "status",
            "next_task",
            "navigation",
            "process_model_identifier",
            "total_tasks",
            "completed_tasks",
            "last_updated",
            "is_review",
            "title",
            "study_id",
            "state",
        ]
        filtered_fields = {key: data[key] for key in keys}
        filtered_fields["next_task"] = TaskSchema().make_task(data["next_task"])
        return ProcessInstanceApi(**filtered_fields)


class ProcessInstanceMetadata:
    """ProcessInstanceMetadata."""

    def __init__(
        self,
        id,
        display_name=None,
        description=None,
        spec_version=None,
        category_id=None,
        category_display_name=None,
        state=None,
        status: ProcessInstanceStatus = None,
        total_tasks=None,
        completed_tasks=None,
        is_review=None,
        display_order=None,
        state_message=None,
        process_model_identifier=None,
    ):
        """__init__."""
        self.id = id
        self.display_name = display_name
        self.description = description
        self.spec_version = spec_version
        self.category_id = category_id
        self.category_display_name = category_display_name
        self.state = state
        self.state_message = state_message
        self.status = status
        self.total_tasks = total_tasks
        self.completed_tasks = completed_tasks
        self.is_review = is_review
        self.display_order = display_order
        self.process_model_identifier = process_model_identifier

    @classmethod
    def from_process_instance(
        cls, process_instance: ProcessInstanceModel, spec: ProcessModelInfo
    ):
        """From_process_instance."""
        instance = cls(
            id=process_instance.id,
            display_name=spec.display_name,
            description=spec.description,
            category_id=spec.category_id,
            category_display_name=spec.category.display_name,
            state_message=process_instance.state_message,
            status=process_instance.status,
            total_tasks=process_instance.total_tasks,
            completed_tasks=process_instance.completed_tasks,
            is_review=spec.is_review,
            display_order=spec.display_order,
            process_model_identifier=process_instance.process_model_identifier,
        )
        return instance


class ProcessInstanceMetadataSchema(Schema):
    """ProcessInstanceMetadataSchema."""

    status = EnumField(ProcessInstanceStatus)

    class Meta:
        """Meta."""

        model = ProcessInstanceMetadata
        additional = [
            "id",
            "display_name",
            "description",
            "state",
            "total_tasks",
            "completed_tasks",
            "display_order",
            "category_id",
            "is_review",
            "category_display_name",
            "state_message",
        ]
        unknown = INCLUDE
