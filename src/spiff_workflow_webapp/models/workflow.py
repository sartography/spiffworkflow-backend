"""Workflow."""
# import enum
#
# import marshmallow
# from crc import db
# from crc import ma
# from marshmallow import post_load
# from sqlalchemy import func
# from sqlalchemy.orm import deferred
#
#
# class WorkflowSpecCategory:
#     """WorkflowSpecCategory."""
#
#     def __init__(self, id, display_name, display_order=0, admin=False):
#         """__init__."""
#         self.id = (
#             id  # A unique string name, lower case, under scores (ie, 'my_category')
#         )
#         self.display_name = display_name
#         self.display_order = display_order
#         self.admin = admin
#         self.workflows = []  # For storing Workflow Metadata
#         self.specs = []  # For the list of specifications associated with a category
#         self.meta = None  # For storing category metadata
#
#     def __eq__(self, other):
#         """__eq__."""
#         if not isinstance(other, WorkflowSpecCategory):
#             return False
#         if other.id == self.id:
#             return True
#         return False
#
#
# class WorkflowSpecCategorySchema(ma.Schema):
#     """WorkflowSpecCategorySchema."""
#
#     class Meta:
#         """Meta."""
#
#         model = WorkflowSpecCategory
#         fields = ["id", "display_name", "display_order", "admin"]
#
#     @post_load
#     def make_cat(self, data, **kwargs):
#         """Make_cat."""
#         return WorkflowSpecCategory(**data)
#
#
# class WorkflowSpecInfo:
#     """WorkflowSpecInfo."""
#
#     def __init__(
#         self,
#         id,
#         display_name,
#         description,
#         is_master_spec=False,
#         standalone=False,
#         library=False,
#         primary_file_name="",
#         primary_process_id="",
#         libraries=None,
#         category_id="",
#         display_order=0,
#         is_review=False,
#     ):
#         """__init__."""
#         self.id = id  # Sting unique id
#         self.display_name = display_name
#         self.description = description
#         self.display_order = display_order
#         self.is_master_spec = is_master_spec
#         self.standalone = standalone
#         self.library = library
#         self.primary_file_name = primary_file_name
#         self.primary_process_id = primary_process_id
#         self.is_review = is_review
#         self.category_id = category_id
#
#         if libraries is None:
#             libraries = []
#         self.libraries = libraries
#
#     def __eq__(self, other):
#         """__eq__."""
#         if not isinstance(other, WorkflowSpecInfo):
#             return False
#         if other.id == self.id:
#             return True
#         return False
#
#
# class WorkflowSpecInfoSchema(ma.Schema):
#     """WorkflowSpecInfoSchema."""
#
#     class Meta:
#         """Meta."""
#
#         model = WorkflowSpecInfo
#
#     id = marshmallow.fields.String(required=True)
#     display_name = marshmallow.fields.String(required=True)
#     description = marshmallow.fields.String()
#     is_master_spec = marshmallow.fields.Boolean(required=True)
#     standalone = marshmallow.fields.Boolean(required=True)
#     library = marshmallow.fields.Boolean(required=True)
#     display_order = marshmallow.fields.Integer(allow_none=True)
#     primary_file_name = marshmallow.fields.String(allow_none=True)
#     primary_process_id = marshmallow.fields.String(allow_none=True)
#     is_review = marshmallow.fields.Boolean(allow_none=True)
#     category_id = marshmallow.fields.String(allow_none=True)
#     libraries = marshmallow.fields.List(marshmallow.fields.String(), allow_none=True)
#
#     @post_load
#     def make_spec(self, data, **kwargs):
#         """Make_spec."""
#         return WorkflowSpecInfo(**data)
#
#
# class WorkflowState(enum.Enum):
#     """WorkflowState."""
#
#     hidden = "hidden"
#     disabled = "disabled"
#     required = "required"
#     optional = "optional"
#     locked = "locked"
#
#     @classmethod
#     def has_value(cls, value):
#         """Has_value."""
#         return value in cls._value2member_map_
#
#     @staticmethod
#     def list():
#         """List."""
#         return list(map(lambda c: c.value, WorkflowState))
#
#
# class WorkflowStatus(enum.Enum):
#     """WorkflowStatus."""
#
#     not_started = "not_started"
#     user_input_required = "user_input_required"
#     waiting = "waiting"
#     complete = "complete"
#     erroring = "erroring"
#
#
# class WorkflowModel(db.Model):
#     """WorkflowModel."""
#
#     __tablename__ = "workflow"
#     id = db.Column(db.Integer, primary_key=True)
#     bpmn_workflow_json = deferred(db.Column(db.JSON))
#     status = db.Column(db.Enum(WorkflowStatus))
#     study_id = db.Column(db.Integer, db.ForeignKey("study.id"))
#     study = db.relationship("StudyModel", backref="workflow", lazy="select")
#     workflow_spec_id = db.Column(db.String)
#     total_tasks = db.Column(db.Integer, default=0)
#     completed_tasks = db.Column(db.Integer, default=0)
#     last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now())
#     user_id = db.Column(db.String, default=None)
#     state = db.Column(db.String, nullable=True)
#     state_message = db.Column(db.String, nullable=True)
