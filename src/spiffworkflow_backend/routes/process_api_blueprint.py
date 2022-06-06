"""APIs for dealing with process groups, process models, and process instances."""
import connexion
import json
from flask import Blueprint
from flask import Response
from flask import g
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.file import FileSchema
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.process_instance import ProcessInstanceApiSchema
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.file import File
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


def add_process_model(body):
    """Add_process_model."""
    spec = ProcessModelInfoSchema().load(body)
    process_model_service = ProcessModelService()
    process_group = process_model_service.get_process_group(spec.process_group_id)
    spec.process_group = process_group
    workflows = process_model_service.cleanup_workflow_spec_display_order(process_group)
    size = len(workflows)
    spec.display_order = size
    process_model_service.add_spec(spec)
    return Response(
        json.dumps(ProcessModelInfoSchema().dump(spec)), status=201, mimetype="application/json"
    )


def get_file(process_model_id, file_name):
    """Get_file."""
    process_model = ProcessModelService().get_spec(process_model_id)
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


def add_file(process_model_id):
    """Add_file."""
    process_model_service = ProcessModelService()
    process_model = process_model_service.get_spec(process_model_id)
    request_file = connexion.request.files["file"]
    file = SpecFileService.add_file(
        process_model, request_file.filename, request_file.stream.read()
    )
    if not process_model.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(process_model, file.name)
        process_model_service.update_spec(process_model)
    return Response(
        json.dumps(FileSchema().dump(file)), status=201, mimetype="application/json"
    )


def create_process_instance(process_model_id):
    """Create_process_instance."""
    process_instance = ProcessInstanceService.create_process_instance(process_model_id, g.user)
    processor = ProcessInstanceProcessor(process_instance)

    processor.do_engine_steps()
    processor.save()
    # ProcessInstanceService.update_task_assignments(processor)

    workflow_api_model = ProcessInstanceService.processor_to_process_instance_api(
        processor
    )
    return Response(
        json.dumps(ProcessInstanceApiSchema().dump(workflow_api_model)), status=201, mimetype="application/json"
    )


def process_groups_list():
    """Process_groups_list."""
    process_groups = ProcessModelService().get_process_groups()
    return ProcessGroupSchema(many=True).dump(process_groups)


def process_group_show(process_group_id):
    """Process_group_show."""
    process_group = ProcessModelService().get_process_group(process_group_id)
    return ProcessGroupSchema().dump(process_group)


def process_model_show(process_model_id):
    """Process_model_show."""
    process_model = ProcessModelService().get_spec(process_model_id)
    if process_model is None:
        raise (
            ApiError(
                code="process_mode_cannot_be_found",
                message=f"Process model cannot be found: {process_model_id}",
                status_code=400,
            )
        )

    files = SpecFileService.get_files(process_model, extension_filter="bpmn")
    process_model.files = files
    process_model_json = ProcessModelInfoSchema().dump(process_model)
    return process_model_json
