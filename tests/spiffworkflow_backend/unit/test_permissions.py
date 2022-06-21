"""Test Permissions."""
from flask_bpmn.models.db import db

from flask.app import Flask
from tests.spiffworkflow_backend.helpers.test_data import find_or_create_user

from spiffworkflow_backend.models.principal import PrincipalModel

# from tests.spiffworkflow_backend.helpers.test_data import find_or_create_process_group
# from spiffworkflow_backend.models.permission_assignment import PermissionAssignmentModel
# from spiffworkflow_backend.models.permission_target import PermissionTargetModel


def test_user_can_be_given_permission_to_administer_process_group(app: Flask) -> None:
    """Test_user_can_be_given_permission_to_administer_process_group."""
    user = find_or_create_user()
    principal = PrincipalModel(user_id=user.id)
    db.session.add(principal)
    db.session.commit()

    # process_group = find_or_create_process_group()
    # permission_target = PermissionTargetModel(process_group_id=process_group.id)
    # db.session.add(permission_target)
    # db.session.commit()
    #
    # permission_assignment = PermissionAssignmentModel(
    #     permission_target_id=permission_target.id,
    #     principal_id=principal.id,
    #     permission="administer",
    #     grant_type="grant",
    # )
    # db.session.add(permission_assignment)
    # db.session.commit()
