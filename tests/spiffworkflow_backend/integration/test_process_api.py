"""Test Process Api Blueprint."""
import io
import json
import time
from typing import Any
from typing import Dict
from typing import Optional

import pytest
from flask.app import Flask
from flask.testing import FlaskClient
from flask_bpmn.models.db import db

from tests.spiffworkflow_backend.helpers.test_data import load_test_spec
from tests.spiffworkflow_backend.helpers.test_data import logged_in_headers
from werkzeug.test import TestResponse

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.helpers.fixture_data import find_or_create_user
from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceStatus
from spiffworkflow_backend.models.process_model import NotificationType
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.process_model_service import ProcessModelService


# phase 1: req_id: 7.1 Deploy process
def test_process_model_add(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_add_new_process_model."""
    # group_id = None,
    model_id = "make_cookies"
    model_display_name = "Cooooookies"
    model_description = "Om nom nom delicious cookies"
    create_process_model(
        client,
        process_group_id=None,
        process_model_id=model_id,
        process_model_display_name=model_display_name,
        process_model_description=model_description,
    )
    process_model = ProcessModelService().get_process_model(model_id)
    assert model_display_name == process_model.display_name
    assert 0 == process_model.display_order
    assert 1 == len(ProcessModelService().get_process_groups())

    create_spec_file(client)


def test_process_model_delete(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_delete."""
    create_process_model(client)

    # assert we have a model
    process_model = ProcessModelService().get_process_model("make_cookies")
    assert process_model is not None
    assert process_model.id == "make_cookies"

    # delete the model
    user = find_or_create_user()
    response = client.delete(
        f"/v1.0/process-models/{process_model.process_group_id}/{process_model.id}",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["ok"] is True

    # assert we no longer have a model
    with pytest.raises(ProcessEntityNotFoundError):
        ProcessModelService().get_process_model("make_cookies")


def test_process_model_delete_with_instances(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_delete_with_instances."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    test_process_group_id = "runs_without_input"
    test_process_model_id = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    # create an instance from a model
    response = create_process_instance(
        client, test_process_group_id, test_process_model_id, headers
    )

    data = json.loads(response.get_data(as_text=True))
    # make sure the instance has the correct model
    assert data["process_model_identifier"] == test_process_model_id

    # try to delete the model
    response = client.delete(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}",
        headers=logged_in_headers(user),
    )

    # make sure we get an error in the response
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert data["code"] == "existing_instances"
    assert (
        data["message"]
        == "We cannot delete the model `sample`, there are existing instances that depend on it."
    )


def test_process_model_update(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_update."""
    create_process_model(client)
    process_model = ProcessModelService().get_process_model("make_cookies")
    assert process_model.id == "make_cookies"
    assert process_model.display_name == "Cooooookies"

    process_model.display_name = "Updated Display Name"

    user = find_or_create_user()
    response = client.put(
        f"/v1.0/process-models/{process_model.process_group_id}/{process_model.id}",
        headers=logged_in_headers(user),
        content_type="application/json",
        data=json.dumps(ProcessModelInfoSchema().dump(process_model)),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["display_name"] == "Updated Display Name"


def test_process_model_list(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_list."""
    # create a group
    group_id = "test_group"
    user = find_or_create_user()
    create_process_group(client, user, group_id)

    # add 5 models to the group
    for i in range(5):
        model_id = f"test_model_{i}"
        model_display_name = f"Test Model {i}"
        model_description = f"Test Model {i} Description"
        create_process_model(
            client, group_id, model_id, model_display_name, model_description
        )

    # get all models
    response = client.get(
        f"/v1.0/process-groups/{group_id}/process-models",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 5
    assert response.json["pagination"]["count"] == 5
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 1

    # get first page, 1 per page
    response = client.get(
        f"/v1.0/process-groups/{group_id}/process-models?page=1&per_page=1",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["id"] == "test_model_0"
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 5

    # get second page, 1 per page
    response = client.get(
        f"/v1.0/process-groups/{group_id}/process-models?page=2&per_page=1",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["id"] == "test_model_1"
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 5

    # get first page, 3 per page
    response = client.get(
        f"/v1.0/process-groups/{group_id}/process-models?page=1&per_page=3",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 3
    assert response.json["results"][0]["id"] == "test_model_0"
    assert response.json["pagination"]["count"] == 3
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 2

    # get second page, 3 per page
    response = client.get(
        f"/v1.0/process-groups/{group_id}/process-models?page=2&per_page=3",
        headers=logged_in_headers(user),
    )
    # there should only be 2 left
    assert response.json is not None
    assert len(response.json["results"]) == 2
    assert response.json["results"][0]["id"] == "test_model_3"
    assert response.json["pagination"]["count"] == 2
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 2


def test_process_group_add(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_add_process_group."""
    process_group = ProcessGroup(
        id="test", display_name="Another Test Category", display_order=0, admin=False
    )
    user = find_or_create_user()
    response = client.post(
        "/v1.0/process-groups",
        headers=logged_in_headers(user),
        content_type="application/json",
        data=json.dumps(ProcessGroupSchema().dump(process_group)),
    )
    assert response.status_code == 201

    # Check what is returned
    result = ProcessGroupSchema().loads(response.get_data(as_text=True))
    assert result is not None
    assert result.display_name == "Another Test Category"
    assert result.id == "test"

    # Check what is persisted
    persisted = ProcessModelService().get_process_group("test")
    assert persisted.display_name == "Another Test Category"
    assert persisted.id == "test"


def test_process_group_delete(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_group_delete."""
    process_group_id = "test"
    process_group_display_name = "My Process Group"

    user = find_or_create_user()
    create_process_group(
        client, user, process_group_id, display_name=process_group_display_name
    )
    persisted = ProcessModelService().get_process_group(process_group_id)
    assert persisted is not None
    assert persisted.id == process_group_id

    client.delete(
        f"/v1.0/process-groups/{process_group_id}", headers=logged_in_headers(user)
    )

    with pytest.raises(ProcessEntityNotFoundError):
        ProcessModelService().get_process_group(process_group_id)


def test_process_group_update(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test Process Group Update."""
    group_id = "test_process_group"
    group_display_name = "Test Group"

    user = find_or_create_user()
    create_process_group(client, user, group_id, display_name=group_display_name)
    process_group = ProcessModelService().get_process_group(group_id)

    assert process_group.display_name == group_display_name

    process_group.display_name = "Modified Display Name"

    response = client.put(
        f"/v1.0/process-groups/{group_id}",
        headers=logged_in_headers(user),
        content_type="application/json",
        data=json.dumps(ProcessGroupSchema().dump(process_group)),
    )
    assert response.status_code == 200

    process_group = ProcessModelService().get_process_group(group_id)
    assert process_group.display_name == "Modified Display Name"


def test_process_group_list(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_group_list."""
    # add 5 groups
    user = find_or_create_user()
    for i in range(5):
        group_id = f"test_process_group_{i}"
        group_display_name = f"Test Group {i}"
        create_process_group(client, user, group_id, display_name=group_display_name)

    # get all groups
    response = client.get(
        "/v1.0/process-groups",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 5
    assert response.json["pagination"]["count"] == 5
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 1

    # get first page, one per page
    response = client.get(
        "/v1.0/process-groups?page=1&per_page=1",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["id"] == "test_process_group_0"
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 5

    # get second page, one per page
    response = client.get(
        "/v1.0/process-groups?page=2&per_page=1",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["id"] == "test_process_group_1"
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 5

    # get first page, 3 per page
    response = client.get(
        "/v1.0/process-groups?page=1&per_page=3",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    assert len(response.json["results"]) == 3
    assert response.json["results"][0]["id"] == "test_process_group_0"
    assert response.json["results"][1]["id"] == "test_process_group_1"
    assert response.json["results"][2]["id"] == "test_process_group_2"
    assert response.json["pagination"]["count"] == 3
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 2

    # get second page, 3 per page
    response = client.get(
        "/v1.0/process-groups?page=2&per_page=3",
        headers=logged_in_headers(user),
    )
    # there should only be 2 left
    assert response.json is not None
    assert len(response.json["results"]) == 2
    assert response.json["results"][0]["id"] == "test_process_group_3"
    assert response.json["results"][1]["id"] == "test_process_group_4"
    assert response.json["pagination"]["count"] == 2
    assert response.json["pagination"]["total"] == 5
    assert response.json["pagination"]["pages"] == 2


def test_process_model_file_update_fails_if_no_file_given(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_file_update."""
    create_spec_file(client)

    spec = load_test_spec("random_fact")
    data = {"key1": "THIS DATA"}
    user = find_or_create_user()
    response = client.put(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/random_fact.svg",
        data=data,
        follow_redirects=True,
        content_type="multipart/form-data",
        headers=logged_in_headers(user),
    )

    assert response.status_code == 400
    assert response.json is not None
    assert response.json["code"] == "no_file_given"


def test_process_model_file_update_fails_if_contents_is_empty(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_file_update."""
    create_spec_file(client)

    spec = load_test_spec("random_fact")
    data = {"file": (io.BytesIO(b""), "random_fact.svg")}
    user = find_or_create_user()
    response = client.put(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/random_fact.svg",
        data=data,
        follow_redirects=True,
        content_type="multipart/form-data",
        headers=logged_in_headers(user),
    )

    assert response.status_code == 400
    assert response.json is not None
    assert response.json["code"] == "file_contents_empty"


def test_process_model_file_update(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_file_update."""
    original_file = create_spec_file(client)

    spec = load_test_spec("random_fact")
    new_file_contents = b"THIS_IS_NEW_DATA"
    data = {"file": (io.BytesIO(new_file_contents), "random_fact.svg")}
    user = find_or_create_user()
    response = client.put(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/random_fact.svg",
        data=data,
        follow_redirects=True,
        content_type="multipart/form-data",
        headers=logged_in_headers(user),
    )

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["ok"]

    response = client.get(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/random_fact.svg",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    updated_file = json.loads(response.get_data(as_text=True))
    assert original_file != updated_file
    assert updated_file["file_contents"] == new_file_contents.decode()


def test_get_file(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_file."""
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}/file/hello_world.bpmn",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["name"] == "hello_world.bpmn"
    assert response.json["process_group_id"] == "group_id1"
    assert response.json["process_model_id"] == "hello_world"


def dest_get_workflow_from_workflow_spec(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_workflow_from_workflow_spec."""
    user = find_or_create_user()
    spec = load_test_spec("hello_world")
    response = client.post(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 201
    assert response.json is not None
    assert "hello_world" == response.json["process_model_identifier"]
    # assert('Task_GetName' == response.json['next_task']['name'])


def test_get_process_groups_when_none(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_process_groups_when_none."""
    user = find_or_create_user()
    response = client.get("/v1.0/process-groups", headers=logged_in_headers(user))
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["results"] == []


def test_get_process_groups_when_there_are_some(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_process_groups_when_there_are_some."""
    user = find_or_create_user()
    load_test_spec("hello_world")
    response = client.get("/v1.0/process-groups", headers=logged_in_headers(user))
    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["total"] == 1
    assert response.json["pagination"]["pages"] == 1


def test_get_process_group_when_found(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_process_group_when_found."""
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-groups/{test_process_group_id}", headers=logged_in_headers(user)
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["id"] == test_process_group_id
    assert response.json["process_models"][0]["id"] == process_model_dir_name


def test_get_process_model_when_found(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_process_model_when_found."""
    user = find_or_create_user()
    test_process_group_id = "group_id1"
    process_model_dir_name = "hello_world"
    load_test_spec(process_model_dir_name, process_group_id=test_process_group_id)
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["id"] == process_model_dir_name
    assert len(response.json["files"]) == 1
    assert response.json["files"][0]["name"] == "hello_world.bpmn"


def test_get_process_model_when_not_found(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_get_process_model_when_not_found."""
    user = find_or_create_user()
    process_model_dir_name = "THIS_NO_EXISTS"
    group_id = create_process_group(client, user, "my_group")
    response = client.get(
        f"/v1.0/process-models/{group_id}/{process_model_dir_name}",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 400
    assert response.json is not None
    assert response.json["code"] == "process_model_cannot_be_found"


def test_process_instance_create(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_create."""
    test_process_group_id = "runs_without_input"
    test_process_model_id = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    response = create_process_instance(
        client, test_process_group_id, test_process_model_id, headers
    )
    assert response.json is not None
    assert response.json["updated_at_in_seconds"] is not None
    assert response.json["status"] == "not_started"
    assert response.json["process_model_identifier"] == test_process_model_id


def test_process_instance_run(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_run."""
    process_group_id = "runs_without_input"
    process_model_id = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    response = create_process_instance(
        client, process_group_id, process_model_id, headers
    )
    assert response.json is not None
    process_instance_id = response.json["id"]
    response = client.post(
        f"/v1.0/process-models/{process_group_id}/{process_model_id}/process-instances/{process_instance_id}/run",
        headers=logged_in_headers(user),
    )

    assert response.json is not None
    assert type(response.json["updated_at_in_seconds"]) is int
    assert response.json["updated_at_in_seconds"] > 0
    assert response.json["status"] == "complete"
    assert response.json["process_model_identifier"] == process_model_id
    assert response.json["data"]["current_user"]["username"] == "test_user1"
    assert response.json["data"]["Mike"] == "Awesome"
    assert response.json["data"]["person"] == "Kevin"


def test_process_instance_list_with_default_list(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_list_with_default_list."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    test_process_group_id = "runs_without_input"
    process_model_dir_name = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )

    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}/process-instances",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["pages"] == 1
    assert response.json["pagination"]["total"] == 1

    process_instance_dict = response.json["results"][0]
    assert type(process_instance_dict["id"]) is int
    assert process_instance_dict["process_model_identifier"] == process_model_dir_name
    assert process_instance_dict["process_group_id"] == test_process_group_id
    assert type(process_instance_dict["start_in_seconds"]) is int
    assert process_instance_dict["start_in_seconds"] > 0
    assert process_instance_dict["end_in_seconds"] is None
    assert process_instance_dict["status"] == "not_started"


def test_process_instance_list_with_paginated_items(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_list_with_paginated_items."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    test_process_group_id = "runs_without_input"
    process_model_dir_name = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )

    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}/process-instances?per_page=2&page=3",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["pages"] == 3
    assert response.json["pagination"]["total"] == 5

    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}/process-instances?per_page=2&page=1",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json["results"]) == 2
    assert response.json["pagination"]["count"] == 2
    assert response.json["pagination"]["pages"] == 3
    assert response.json["pagination"]["total"] == 5


def test_process_instance_list_filter(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_list_filter."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    test_process_group_id = "runs_without_input"
    test_process_model_id = "sample"
    user = find_or_create_user()
    load_test_spec(test_process_model_id, process_group_id=test_process_group_id)

    statuses = [status.value for status in ProcessInstanceStatus]
    # create 5 instances with different status, and different start_in_seconds/end_in_seconds
    for i in range(5):
        process_instance = ProcessInstanceModel(
            status=ProcessInstanceStatus[statuses[i]].value,
            process_initiator=user,
            process_model_identifier=test_process_model_id,
            process_group_identifier=test_process_group_id,
            updated_at_in_seconds=round(time.time()),
            start_in_seconds=(1000 * i) + 1000,
            end_in_seconds=(1000 * i) + 2000,
            bpmn_json=json.dumps({"i": i}),
        )
        db.session.add(process_instance)
    db.session.commit()

    # Without filtering we should get all 5 instances
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    results = response.json["results"]
    assert len(results) == 5

    # filter for each of the status
    # we should get 1 instance each time
    for i in range(5):
        response = client.get(
            f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances?process_status={ProcessInstanceStatus[statuses[i]].value}",
            headers=logged_in_headers(user),
        )
        assert response.json is not None
        results = response.json["results"]
        assert len(results) == 1
        assert results[0]["status"] == ProcessInstanceStatus[statuses[i]].value

    # filter by start/end seconds
    # start > 1000 - this should eliminate the first
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances?start_from=1001",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    results = response.json["results"]
    assert len(results) == 4
    for i in range(4):
        assert json.loads(results[i]["bpmn_json"])["i"] in (1, 2, 3, 4)

    # start > 2000, end < 5000 - this should eliminate the first 2 and the last
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances?start_from=2001&end_till=5999",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    results = response.json["results"]
    assert len(results) == 2
    assert json.loads(results[0]["bpmn_json"])["i"] in (2, 3)
    assert json.loads(results[1]["bpmn_json"])["i"] in (2, 3)

    # start > 1000, start < 4000 - this should eliminate the first and the last 2
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances?start_from=1001&start_till=3999",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    results = response.json["results"]
    assert len(results) == 2
    assert json.loads(results[0]["bpmn_json"])["i"] in (1, 2)
    assert json.loads(results[1]["bpmn_json"])["i"] in (1, 2)

    # end > 2000, end < 6000 - this should eliminate the first and the last
    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances?end_from=2001&end_till=5999",
        headers=logged_in_headers(user),
    )
    assert response.json is not None
    results = response.json["results"]
    assert len(results) == 3
    for i in range(3):
        assert json.loads(results[i]["bpmn_json"])["i"] in (1, 2, 3)


def test_process_instance_report_with_default_list(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_instance_report_with_default_list."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    test_process_group_id = "runs_without_input"
    process_model_dir_name = "sample"
    user = find_or_create_user()
    headers = logged_in_headers(user)
    create_process_instance(
        client, test_process_group_id, process_model_dir_name, headers
    )

    response = client.get(
        f"/v1.0/process-models/{test_process_group_id}/{process_model_dir_name}/process-instances/report",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json["results"]) == 1
    assert response.json["pagination"]["count"] == 1
    assert response.json["pagination"]["pages"] == 1
    assert response.json["pagination"]["total"] == 1

    process_instance_dict = response.json["results"][0]
    assert type(process_instance_dict["id"]) is int
    assert process_instance_dict["process_model_identifier"] == process_model_dir_name
    assert process_instance_dict["process_group_id"] == test_process_group_id
    assert type(process_instance_dict["start_in_seconds"]) is int
    assert process_instance_dict["start_in_seconds"] > 0
    assert process_instance_dict["end_in_seconds"] is None
    assert process_instance_dict["status"] == "not_started"


def setup_testing_instance(client, process_group_id, process_model_id, user):

    headers = logged_in_headers(user)
    response = create_process_instance(
        client, process_group_id, process_model_id, headers
    )
    process_instance_id = response.json["id"]
    return process_instance_id


def test_error_handler(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_error_handler."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    process_group_id = "data"
    process_model_id = "error"
    user = find_or_create_user()

    process_instance_id = setup_testing_instance(client, process_group_id, process_model_id, user)
    process = (
        db.session.query(ProcessInstanceModel)
        .filter(ProcessInstanceModel.id == process_instance_id)
        .first()
    )
    assert process.status == "not_started"

    response = client.post(
        f"/v1.0/process-models/{process_group_id}/{process_model_id}/process-instances/{process_instance_id}/run",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 400

    api_error = json.loads(response.get_data(as_text=True))
    assert api_error["code"] == "unknown_exception"
    assert "An unknown error occurred." in api_error["message"]
    assert (
        'Original error: ApiError: Activity_CauseError: TypeError:can only concatenate str (not "int") to str.'
        in api_error["message"]
    )
    assert "Error in task 'Cause Error' (Activity_CauseError)." in api_error["message"]
    assert "Error is on line 1. In file error.bpmn." in api_error["message"]

    process = (
        db.session.query(ProcessInstanceModel)
        .filter(ProcessInstanceModel.id == process_instance_id)
        .first()
    )
    assert process.status == "faulted"


def test_error_handler_with_email(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_error_handler."""
    db.session.query(ProcessInstanceModel).delete()
    db.session.commit()

    process_group_id = "data"
    process_model_id = "error"
    user = find_or_create_user()

    process_instance_id = setup_testing_instance(client, process_group_id, process_model_id, user)

    process_model = ProcessModelService().get_process_model(process_model_id, process_group_id)
    process_model.exception_notification_addresses = ['user@example.com',]
    ProcessModelService().update_spec(process_model)

    mail = app.config["MAIL_APP"]
    with mail.record_messages() as outbox:

        response = client.post(
            f"/v1.0/process-models/{process_group_id}/{process_model_id}/process-instances/{process_instance_id}/run",
            headers=logged_in_headers(user),
        )
        assert response.status_code == 400
        assert len(outbox) == 1
        message = outbox[0]
        assert message.subject == 'Unexpected error in app'
        assert message.body == 'Activity_CauseError: TypeError:can only concatenate str (not "int") to str'
        assert message.recipients == process_model.exception_notification_addresses

    process = (
        db.session.query(ProcessInstanceModel)
        .filter(ProcessInstanceModel.id == process_instance_id)
        .first()
    )
    assert process.status == "faulted"


def test_process_model_file_create(
    app: Flask, client: FlaskClient, with_bpmn_file_cleanup: None
) -> None:
    """Test_process_model_file_create."""
    process_group_id = "hello_world"
    process_model_id = "hello_world"
    file_name = "hello_world.svg"
    file_data = b"abc123"

    result = create_spec_file(
        client,
        process_group_id=process_group_id,
        process_model_id=process_model_id,
        file_name=file_name,
        file_data=file_data,
    )
    assert result["process_group_id"] == process_group_id
    assert result["process_model_id"] == process_model_id
    assert result["name"] == file_name
    assert bytes(str(result["file_contents"]), "utf-8") == file_data


def create_process_instance(
    client: FlaskClient,
    test_process_group_id: str,
    test_process_model_id: str,
    headers: Dict[str, str],
) -> TestResponse:
    """Create_process_instance."""
    load_test_spec(test_process_model_id, process_group_id=test_process_group_id)
    response = client.post(
        f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}",
        headers=headers,
    )
    assert response.status_code == 201
    return response


def create_process_model(
    client: FlaskClient,
    process_group_id: Optional[str] = None,
    process_model_id: Optional[str] = None,
    process_model_display_name: Optional[str] = None,
    process_model_description: Optional[str] = None,
    fault_or_suspend_on_exception: Optional[str] = None,
    exception_notification_addresses: Optional[list] = None,
    primary_process_id: str = None,
    primary_file_name: str = None,
) -> TestResponse:
    """Create_process_model."""
    process_model_service = ProcessModelService()

    # make sure we have a group
    if process_group_id is None:
        process_group_tmp = ProcessGroup(
            id="test_cat", display_name="Test Category", display_order=0, admin=False
        )
        process_group = process_model_service.add_process_group(process_group_tmp)
    else:
        process_group = ProcessModelService().get_process_group(process_group_id)

    if process_model_id is None:
        process_model_id = "make_cookies"
    if process_model_display_name is None:
        process_model_display_name = "Cooooookies"
    if process_model_description is None:
        process_model_description = "Om nom nom delicious cookies"
    if fault_or_suspend_on_exception is None:
        fault_or_suspend_on_exception = NotificationType.suspend.value
    if exception_notification_addresses is None:
        exception_notification_addresses = []
    if primary_process_id is None:
        primary_process_id = ''
    if primary_file_name is None:
        primary_file_name = ''
    model = ProcessModelInfo(
        id=process_model_id,
        display_name=process_model_display_name,
        description=process_model_description,
        process_group_id=process_group.id,
        standalone=False,
        is_review=False,
        is_master_spec=False,
        libraries=[],
        library=False,
        primary_process_id=primary_process_id,
        primary_file_name=primary_file_name,
        fault_or_suspend_on_exception=fault_or_suspend_on_exception,
        exception_notification_addresses=exception_notification_addresses,
    )
    user = find_or_create_user()
    response = client.post(
        "/v1.0/process-models",
        content_type="application/json",
        data=json.dumps(ProcessModelInfoSchema().dump(model)),
        headers=logged_in_headers(user),
    )
    assert response.status_code == 201
    return response


def create_spec_file(
    client: FlaskClient,
    process_group_id: str = "",
    process_model_id: str = "",
    file_name: str = "",
    file_data: bytes = b"",
) -> Any:
    """Test_create_spec_file."""
    if process_group_id == "":
        process_group_id = "random_fact"
    if process_model_id == "":
        process_model_id = "random_fact"
    if file_name == "":
        file_name = "random_fact.svg"
    if file_data == b"":
        file_data = b"abcdef"
    spec = load_test_spec(process_model_id, process_group_id=process_group_id)
    data = {"file": (io.BytesIO(file_data), file_name)}
    user = find_or_create_user()
    response = client.post(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file",
        data=data,
        follow_redirects=True,
        content_type="multipart/form-data",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 201
    assert response.get_data() is not None
    file = json.loads(response.get_data(as_text=True))
    # assert FileType.svg.value == file["type"]
    # assert "image/svg+xml" == file["content_type"]

    response = client.get(
        f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/{file_name}",
        headers=logged_in_headers(user),
    )
    assert response.status_code == 200
    file2 = json.loads(response.get_data(as_text=True))
    assert file["file_contents"] == file2["file_contents"]
    return file


def create_process_group(
    client: FlaskClient, user: Any, process_group_id: str, display_name: str = ""
) -> str:
    """Create_process_group."""
    process_group = ProcessGroup(
        id=process_group_id, display_name=display_name, display_order=0, admin=False
    )
    response = client.post(
        "/v1.0/process-groups",
        headers=logged_in_headers(user),
        content_type="application/json",
        data=json.dumps(ProcessGroupSchema().dump(process_group)),
    )
    assert response.status_code == 201
    assert response.json is not None
    assert response.json["id"] == process_group_id
    return process_group_id


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
