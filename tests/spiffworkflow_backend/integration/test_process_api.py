"""Test Process Api Blueprint."""
import io
import json
import os
import shutil

import pytest
from flask.testing import FlaskClient
from tests.spiffworkflow_backend.helpers.test_data import find_or_create_user
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec
from tests.spiffworkflow_backend.helpers.test_data import logged_in_headers

from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.process_model_service import ProcessModelService


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
#     response = client.get('/v1.0/workflow-specification/random_fact', headers=logged_in_headers())
#     assert_success(response)
#     json_data = json.loads(response.get_data(as_text=True))
#     api_spec = WorkflowSpecInfoSchema().load(json_data)
#
#     fs_spec = process_model_service.get_spec('random_fact')
#     assert(WorkflowSpecInfoSchema().dump(fs_spec) == json_data)
#


def test_get_file(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(app, process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-models/{process_model_dir_name}/file/hello_world.bpmn", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert response.json["name"] == "hello_world.bpmn"
    assert response.json["process_group_id"] == "group_id1"
    assert response.json["process_model_id"] == "hello_world"


def test_get_workflow_from_workflow_spec(
    app, client: FlaskClient, with_bpmn_file_cleanup
):
    """Test_get_workflow_from_workflow_spec."""
    user = find_or_create_user()
    spec = load_test_spec(app, "hello_world")
    response = client.post(
        f"/v1.0/workflow-specification/{spec.id}", headers=logged_in_headers(user)
    )
    assert response.status_code == 201
    assert "hello_world" == response.json["process_model_identifier"]
    # assert('Task_GetName' == response.json['next_task']['name'])


def test_get_process_groups_when_none(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    response = client.get(
        "/v1.0/process-groups", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert response.json == []


def test_get_process_groups_when_there_are_some(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    load_test_spec(app, "hello_world")
    response = client.get(
        "/v1.0/process-groups", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert len(response.json) == 1


def test_get_process_group_when_found(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(app, process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-groups/{test_process_group_id}", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert response.json["id"] == test_process_group_id
    assert response.json["process_models"][0]["id"] == process_model_dir_name


def test_get_process_model_when_found(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(app, process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-models/{process_model_dir_name}", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert response.json["id"] == process_model_dir_name
    assert len(response.json["files"]) == 1
    assert response.json["files"][0]["name"] == "hello_world.bpmn"


def test_get_process_model_when_not_found(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    process_model_dir_name = "THIS_NO_EXISTS"
    response = client.get(
        f"/v1.0/process-models/{process_model_dir_name}", headers=logged_in_headers(user)
    )
    assert response.status_code == 400
    assert response.json["code"] == "process_mode_cannot_be_found"


def test_process_instance_create(app, client: FlaskClient, with_bpmn_file_cleanup):
    user = find_or_create_user()
    test_process_group_id = "runs_without_input"
    process_model_dir_name = "sample"
    load_test_spec(app, process_model_dir_name, process_group_id=test_process_group_id)
    response = client.post(
        f"/v1.0/process-models/{process_model_dir_name}", headers=logged_in_headers(user)
    )
    assert response.status_code == 201
    assert response.json["status"] == "complete"
    assert response.json["process_model_identifier"] == "sample"
    assert response.json["data"]["current_user"]["username"] == "test_user1"
    assert response.json["data"]["Mike"] == "Awesome"
    assert response.json["data"]["person"] == "Kevin"


def create_process_model(app, client: FlaskClient):
    """Create_process_model."""
    process_model_service = ProcessModelService()
    assert 0 == len(process_model_service.get_specs())
    assert 0 == len(process_model_service.get_process_groups())
    process_group = ProcessGroup(
        id="test_cat", display_name="Test Category", display_order=0, admin=False
    )
    process_model_service.add_process_group(process_group)
    spec = ProcessModelInfo(
        id="make_cookies",
        display_name="Cooooookies",
        description="Om nom nom delicious cookies",
        process_group_id=process_group.id,
        standalone=False,
        is_review=False,
        is_master_spec=False,
        libraries=[],
        library=False,
        primary_process_id="",
        primary_file_name="",
    )
    user = find_or_create_user()
    response = client.post(
        "/v1.0/workflow-specification",
        content_type="application/json",
        data=json.dumps(ProcessModelInfoSchema().dump(spec)),
        headers=logged_in_headers(user),
    )
    assert response.status_code == 201

    fs_spec = process_model_service.get_spec("make_cookies")
    assert spec.display_name == fs_spec.display_name
    assert 0 == fs_spec.display_order
    assert 1 == len(process_model_service.get_process_groups())


def create_spec_file(app, client: FlaskClient):
    """Test_create_spec_file."""
    spec = load_test_spec(app, "random_fact")
    data = {"file": (io.BytesIO(b"abcdef"), "random_fact.svg")}
    user = find_or_create_user()
    response = client.post(
        "/v1.0/workflow-specification/%s/file" % spec.id,
        data=data,
        follow_redirects=True,
        content_type="multipart/form-data",
        headers=logged_in_headers(user),
    )

    assert response.status_code == 201
    assert response.get_data() is not None
    file = json.loads(response.get_data(as_text=True))
    assert FileType.svg.value == file["type"]
    assert "image/svg+xml" == file["content_type"]

    response = client.get(
        f"/v1.0/workflow-specification/{spec.id}/file/random_fact.svg",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    file2 = json.loads(response.get_data(as_text=True))
    assert file == file2
