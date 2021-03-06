"""User."""
from typing import Dict
from typing import Optional

from tests.spiffworkflow_backend.helpers.example_data import ExampleDataLoader

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_model_service import ProcessModelService


def assure_process_group_exists(process_group_id: Optional[str] = None) -> ProcessGroup:
    """Assure_process_group_exists."""
    process_group = None
    workflow_spec_service = ProcessModelService()
    if process_group_id is not None:
        try:
            process_group = workflow_spec_service.get_process_group(process_group_id)
        except ProcessEntityNotFoundError:
            process_group = None

    if process_group is None:
        process_group_id_to_create = "test_process_group"
        if process_group_id is not None:
            process_group_id_to_create = process_group_id
        process_group = ProcessGroup(
            id=process_group_id_to_create,
            display_name="Test Workflows",
            admin=False,
            display_order=0,
        )
        workflow_spec_service.add_process_group(process_group)
    return process_group


def load_test_spec(
    process_model_id: str,
    master_spec: bool = False,
    process_group_id: Optional[str] = None,
    library: bool = False,
) -> ProcessModelInfo:
    """Loads a process model into the bpmn dir based on a directory in tests/data."""
    process_group = None
    workflow_spec_service = ProcessModelService()
    if process_group_id is None:
        process_group_id = "test_process_group_id"
    if not master_spec and not library:
        process_group = assure_process_group_exists(process_group_id)
        process_group_id = process_group.id

    try:
        return workflow_spec_service.get_process_model(
            process_model_id, group_id=process_group_id
        )
    except ProcessEntityNotFoundError:
        spec = ExampleDataLoader().create_spec(
            id=process_model_id,
            master_spec=master_spec,
            from_tests=True,
            display_name=process_model_id,
            process_group_id=process_group_id,
            library=library,
        )
        return spec


# def user_info_to_query_string(user_info, redirect_url):
#     query_string_list = []
#     items = user_info.items()
#     for key, value in items:
#         query_string_list.append('%s=%s' % (key, urllib.parse.quote(value)))
#
#     query_string_list.append('redirect_url=%s' % redirect_url)
#
#     return '?%s' % '&'.join(query_string_list)


def logged_in_headers(
    user: UserModel, _redirect_url: str = "http://some/frontend/url"
) -> Dict[str, str]:
    """Logged_in_headers."""
    # if user is None:
    #     uid = 'test_user'
    #     user_info = {'uid': 'test_user'}
    # else:
    #     uid = user.uid
    #     user_info = {'uid': user.uid}

    # query_string = user_info_to_query_string(user_info, redirect_url)
    # rv = self.app.get("/v1.0/login%s" % query_string, follow_redirects=False)
    # self.assertTrue(rv.status_code == 302)
    # self.assertTrue(str.startswith(rv.location, redirect_url))
    #
    # user_model = session.query(UserModel).filter_by(uid=uid).first()
    # self.assertIsNotNone(user_model.ldap_info.display_name)
    # self.assertEqual(user_model.uid, uid)
    # self.assertTrue('user' in g, 'User should be in Flask globals')
    # user = UserService.current_user(allow_admin_impersonate=True)
    # self.assertEqual(uid, user.uid, 'Logged in user should match given user uid')

    return dict(Authorization="Bearer " + user.encode_auth_token())
