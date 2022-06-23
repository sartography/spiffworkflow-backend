"""Load_database_models."""
"""Loads and sets up all database models for SQLAlchemy.

autoflake8 will remove these lines without the noqa comment
"""
from flask_bpmn.models.db import add_listeners

from spiffworkflow_backend.models.data_store import DataStoreModel  # noqa: F401
from spiffworkflow_backend.models.file import FileModel  # noqa: F401
from spiffworkflow_backend.models.principal import PrincipalModel  # noqa: F401
from spiffworkflow_backend.models.process_instance import (
    ProcessInstanceModel,
)  # noqa: F401
from spiffworkflow_backend.models.process_instance_report import (
    ProcessInstanceReportModel,
)  # noqa: F401
from spiffworkflow_backend.models.task_event import TaskEventModel  # noqa: F401
from spiffworkflow_backend.models.user import UserModel  # noqa: F401
from spiffworkflow_backend.models.user_group_assignment import (
    UserGroupAssignmentModel,
)  # noqa: F401

# from spiffworkflow_backend.models.permission_assignment import PermissionAssignmentModel  # noqa: F401
# from spiffworkflow_backend.models.permission_target import PermissionTargetModel  # noqa: F401

add_listeners()
