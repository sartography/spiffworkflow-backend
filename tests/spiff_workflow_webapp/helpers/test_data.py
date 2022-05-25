"""User."""
import os


from spiff_workflow_webapp.models.process_group import ProcessGroup
from spiff_workflow_webapp.services.process_model_service import ProcessModelService

from tests.spiff_workflow_webapp.helpers.example_data import ExampleDataLoader


# def find_or_create_user(username: str = "test_user1") -> Any:
#     user = UserModel.query.filter_by(username=username).first()
#     if user is None:
#         user = UserModel(username=username)
#         db.session.add(user)
#         db.session.commit()
#
#     return user
#
#
# def find_or_create_process_group(name: str = "test_group1") -> Any:
#     process_group = ProcessGroupModel.query.filter_by(name=name).first()
#     if process_group is None:
#         process_group = ProcessGroupModel(name=name)
#         db.session.add(process_group)
#         db.session.commit()
#
#     return process_group


def assure_process_group_exists(process_group_id=None):
    """Assure_process_group_exists."""
    process_group = None
    workflow_spec_service = ProcessModelService()
    if process_group_id is not None:
        process_group = workflow_spec_service.get_process_group(process_group_id)
    if process_group is None:
        process_group = ProcessGroup(id="test_process_group", display_name="Test Workflows", admin=False, display_order=0)
        workflow_spec_service.add_process_group(process_group)
    return process_group


def load_test_spec(app, dir_name, display_name=None, master_spec=False, process_group_id=None, library=False):
    """Loads a spec into the database based on a directory in /tests/data."""
    process_group = None
    workflow_spec_service = ProcessModelService()
    if not master_spec and not library:
        process_group = assure_process_group_exists(process_group_id)
        process_group_id = process_group.id
    workflow_spec = workflow_spec_service.get_spec(dir_name)
    if workflow_spec:
        return workflow_spec
    else:
        filepath = os.path.join(app.root_path, '..', 'tests', 'data', dir_name, "*")
        if display_name is None:
            display_name = dir_name
        spec = ExampleDataLoader().create_spec(id=dir_name, filepath=filepath, master_spec=master_spec,
                                               display_name=display_name, process_group_id=process_group_id, library=library)
        return spec
