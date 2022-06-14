"""APIs for dealing with process groups, process models, and process instances."""
import json

import connexion  # type: ignore
from flask import Blueprint
from flask import g
from flask import Response
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.file import FileSchema
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceApiSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.spec_file_service import SpecFileService

# from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
# from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
# from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

process_api_blueprint = Blueprint("process_api", __name__)


def process_group_add(body):
    """Add_process_group."""
    # just so the import is used. oh, and it's imported because spiffworkflow_backend/unit/test_permissions.py
    # depends on it, and otherwise flask migrations won't include it in the list of database tables.
    PrincipalModel()

    process_model_service = ProcessModelService()
    process_group = ProcessGroupSchema().load(body)
    process_model_service.add_process_group(process_group)
    return Response(
        json.dumps(ProcessGroupSchema().dump(process_group)),
        status=201,
        mimetype="application/json",
    )


def process_group_delete(process_group_id):
    """Process_group_delete."""
    ProcessModelService().process_group_delete(process_group_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_group_update(process_group_id, body):
    """Process Group Update."""
    process_group = ProcessGroupSchema().load(body)
    ProcessModelService().update_process_group(process_group)
    return ProcessGroupSchema().dump(process_group)


def process_groups_list():
    """Process_groups_list."""
    process_groups = ProcessModelService().get_process_groups()
    return ProcessGroupSchema(many=True).dump(process_groups)


def process_group_show(process_group_id):
    """Process_group_show."""
    process_group = ProcessModelService().get_process_group(process_group_id)
    return ProcessGroupSchema().dump(process_group)


def process_model_add(body):
    """Add_process_model."""
    process_model_info = ProcessModelInfoSchema().load(body)
    process_model_service = ProcessModelService()
    process_group = process_model_service.get_process_group(
        process_model_info.process_group_id
    )
    process_model_info.process_group = process_group
    workflows = process_model_service.cleanup_workflow_spec_display_order(process_group)
    size = len(workflows)
    process_model_info.display_order = size
    process_model_service.add_spec(process_model_info)
    return Response(
        json.dumps(ProcessModelInfoSchema().dump(process_model_info)),
        status=201,
        mimetype="application/json",
    )


def process_model_delete(process_group_id, process_model_id):
    """Process_model_delete."""
    ProcessModelService().process_model_delete(process_model_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_model_update(process_group_id, process_model_id, body):
    """Process_model_update."""
    process_model = ProcessModelInfoSchema().load(body)
    ProcessModelService().update_spec(process_model)
    return ProcessModelInfoSchema().dump(process_model)


def process_model_show(process_group_id, process_model_id):
    """Process_model_show."""
    process_model = ProcessModelService().get_process_model(process_model_id, process_group_id)
    if process_model is None:
        raise (
            ApiError(
                code="process_mode_cannot_be_found",
                message=f"Process model cannot be found: {process_model_id}",
                status_code=400,
            )
        )

    files = sorted(SpecFileService.get_files(process_model))
    process_model.files = files
    process_model_json = ProcessModelInfoSchema().dump(process_model)
    return process_model_json


def get_file(process_model_id, file_name):
    """Get_file."""
    process_model = ProcessModelService().get_process_model(process_model_id)
    files = SpecFileService.get_files(process_model, file_name)
    if len(files) == 0:
        raise ApiError(
            code="unknown file",
            message=f"No information exists for file {file_name}"
            f" it does not exist in workflow {process_model_id}.",
            status_code=404,
        )

    file = files[0]
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    return FileSchema().dump(file)


def process_model_file_update(process_model_id, file_name):
    """Process_model_file_save."""
    process_model = ProcessModelService().get_process_model(process_model_id)

    request_file = get_file_from_request()
    request_file_contents = request_file.stream.read()
    if not request_file_contents:
        raise ApiError(
            code="file_contents_empty",
            message="Given request file does not have any content",
            status_code=400,
        )

    SpecFileService.update_file(process_model, file_name, request_file_contents)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def add_file(process_model_id):
    """Add_file."""
    process_model_service = ProcessModelService()
    process_model = process_model_service.get_process_model(process_model_id)
    request_file = get_file_from_request()
    file = SpecFileService.add_file(
        process_model, request_file.filename, request_file.stream.read()
    )
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    if not process_model.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(process_model, file.name)
        process_model_service.update_spec(process_model)
    return Response(
        json.dumps(FileSchema().dump(file)), status=201, mimetype="application/json"
    )


def process_instance_create(process_group_id, process_model_id):
    """Create_process_instance."""
    process_instance = ProcessInstanceService.create_process_instance(
        process_model_id, g.user
    )
    processor = ProcessInstanceProcessor(process_instance)

    processor.do_engine_steps()
    processor.save()
    # ProcessInstanceService.update_task_assignments(processor)

    process_instance_api = ProcessInstanceService.processor_to_process_instance_api(
        processor
    )
    process_instance_data = processor.get_data()
    process_instance_metadata = ProcessInstanceApiSchema().dump(process_instance_api)
    process_instance_metadata["data"] = process_instance_data
    return Response(
        json.dumps(process_instance_metadata), status=201, mimetype="application/json"
    )


def process_instance_list(process_model_id, page=1, per_page=100):
    """Process_instance_list."""
    process_model = ProcessModelService().get_process_model(process_model_id)
    if process_model is None:
        raise (
            ApiError(
                code="process_mode_cannot_be_found",
                message=f"Process model cannot be found: {process_model_id}",
                status_code=400,
            )
        )

    process_instances = (
        ProcessInstanceModel.query.filter_by(process_model_identifier=process_model.id)
        .order_by(
            ProcessInstanceModel.start_in_seconds.desc(), ProcessInstanceModel.id.desc()
        )
        .paginate(page, per_page, False)
    )

    serialized_results = []
    for process_instance in process_instances.items:
        process_instance_serialized = process_instance.serialized
        process_instance_serialized["process_group_id"] = process_model.process_group_id
        serialized_results.append(process_instance_serialized)

    response_json = {
        "results": serialized_results,
        "pagination": {
            "count": len(process_instances.items),
            "total": process_instances.total,
            "pages": process_instances.pages,
        },
    }
    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def get_file_from_request():
    """Get_file_from_request."""
    request_file = connexion.request.files.get("file")
    if not request_file:
        raise ApiError(
            code="no_file_given",
            message="Given request does not contain a file",
            status_code=400,
        )
    return request_file
