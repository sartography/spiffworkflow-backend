"""Loads and sets up all database models for SQLAlchemy."""

from flask_bpmn.models.db import add_listeners  # type: ignore

from spiffworkflow_backend.models.data_store import DataStoreModel
from spiffworkflow_backend.models.file import FileModel
# from spiffworkflow_backend.models.permission_assignment import PermissionAssignmentModel
# from spiffworkflow_backend.models.permission_target import PermissionTargetModel
from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance_report import ProcessInstanceReportModel
from spiffworkflow_backend.models.task_event import TaskEventModel
from spiffworkflow_backend.models.user_group_assignment import UserGroupAssignmentModel
from spiffworkflow_backend.models.user import UserModel

add_listeners()
