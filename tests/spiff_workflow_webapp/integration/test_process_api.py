"""Test Process Api Blueprint."""
import json
import pytest
import os
import shutil

from typing import Union

from flask.testing import FlaskClient
from flask_bpmn.models.db import db

from spiff_workflow_webapp.models.process_instance import ProcessInstanceModel
from spiff_workflow_webapp.models.process_model import ProcessModelInfoSchema, ProcessModelInfo
from spiff_workflow_webapp.models.process_group import ProcessGroup
from spiff_workflow_webapp.services.process_model_service import ProcessModelService


@pytest.fixture()
def process_group_resource():
    print("setup")
    process_model_service = ProcessModelService()
    bpmn_root_path_test_cat = os.path.join(process_model_service.root_path(), "test_cat")
    if os.path.exists(bpmn_root_path_test_cat):
        shutil.rmtree(bpmn_root_path_test_cat)

    yield "resource"

    print("teardown")
    if os.path.exists(bpmn_root_path_test_cat):
        shutil.rmtree(bpmn_root_path_test_cat)


def test_add_new_process_modelification(client: FlaskClient, process_group_resource):
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

# def test_get_process_modelification(self):
#
#     load_test_spec('random_fact')
#     rv = app.get('/v1.0/workflow-specification/random_fact', headers=logged_in_headers())
#     assert_success(rv)
#     json_data = json.loads(rv.get_data(as_text=True))
#     api_spec = WorkflowSpecInfoSchema().load(json_data)
#
#     fs_spec = process_model_service.get_spec('random_fact')
#     assert(WorkflowSpecInfoSchema().dump(fs_spec) == json_data)
#
