"""Test Process Api Blueprint."""
import json
import pytest
import os
import io
import shutil


from flask.testing import FlaskClient

from spiff_workflow_webapp.models.process_model import ProcessModelInfoSchema, ProcessModelInfo
from spiff_workflow_webapp.models.process_group import ProcessGroup
from spiff_workflow_webapp.services.process_model_service import ProcessModelService
from spiff_workflow_webapp.models.file import FileType

from tests.spiff_workflow_webapp.helpers.test_data import load_test_spec, find_or_create_user, logged_in_headers


@pytest.fixture()
def with_bpmn_file_cleanup():
    """Process_group_resource."""
    try:
        yield
    finally:
        process_model_service = ProcessModelService()
        if os.path.exists(process_model_service.root_path()):
            shutil.rmtree(process_model_service.root_path())


# phase 1: req_id: 7.1 Deploy process
def test_add_new_process_model(app, client: FlaskClient, with_bpmn_file_cleanup):
    """Test_add_new_process_model."""
    create_process_model(app, client)
    create_spec_file(app, client)

# def test_get_process_model(self):
#
#     load_test_spec('random_fact')
#     rv = client.get('/v1.0/workflow-specification/random_fact', headers=logged_in_headers())
#     assert_success(rv)
#     json_data = json.loads(rv.get_data(as_text=True))
#     api_spec = WorkflowSpecInfoSchema().load(json_data)
#
#     fs_spec = process_model_service.get_spec('random_fact')
#     assert(WorkflowSpecInfoSchema().dump(fs_spec) == json_data)
#


def test_get_workflow_from_workflow_spec(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    spec = load_test_spec(app, 'hello_world')
    rv = client.post(f'/v1.0/workflow-specification/{spec.id}', headers=logged_in_headers(user))
    assert rv.status_code == 200
    assert('hello_world' == rv.json['workflow_spec_id'])
    assert('Task_GetName' == rv.json['next_task']['name'])


def create_process_model(app, client: FlaskClient):
    process_model_service = ProcessModelService()
    assert(0 == len(process_model_service.get_specs()))
    assert(0 == len(process_model_service.get_process_groups()))
    cat = ProcessGroup(id="test_cat", display_name="Test Category", display_order=0, admin=False)
    process_model_service.add_process_group(cat)
    spec = ProcessModelInfo(id='make_cookies', display_name='Cooooookies',
                            description='Om nom nom delicious cookies', process_group_id=cat.id,
                            standalone=False, is_review=False, is_master_spec=False, libraries=[], library=False,
                            primary_process_id='', primary_file_name='')
    rv = client.post('/v1.0/workflow-specification',
                     # headers=logged_in_headers(),
                     content_type="application/json",
                     data=json.dumps(ProcessModelInfoSchema().dump(spec)))
    assert rv.status_code == 200

    fs_spec = process_model_service.get_spec('make_cookies')
    assert(spec.display_name == fs_spec.display_name)
    assert(0 == fs_spec.display_order)
    assert(1 == len(process_model_service.get_process_groups()))

def create_spec_file(app, client: FlaskClient):
    """Test_create_spec_file."""
    spec = load_test_spec(app, 'random_fact')
    data = {'file': (io.BytesIO(b"abcdef"), 'random_fact.svg')}
    rv = client.post('/v1.0/workflow-specification/%s/file' % spec.id, data=data, follow_redirects=True, content_type='multipart/form-data')

    assert rv.status_code == 200
    assert(rv.get_data() is not None)
    file = json.loads(rv.get_data(as_text=True))
    assert(FileType.svg.value == file['type'])
    assert("image/svg+xml" == file['content_type'])

    rv = client.get(f'/v1.0/workflow-specification/{spec.id}/file/random_fact.svg')
    assert rv.status_code == 200
    file2 = json.loads(rv.get_data(as_text=True))
    assert(file == file2)
