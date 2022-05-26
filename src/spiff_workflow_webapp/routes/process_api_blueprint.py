"""APIs for dealing with process groups, process models, and process instances."""

import connexion
from flask import Blueprint

# from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
# from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
# from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

from flask_bpmn.api.api_error import ApiError

from spiff_workflow_webapp.models.process_model import ProcessModelInfoSchema
from spiff_workflow_webapp.models.process_instance import ProcessInstanceApiSchema
from spiff_workflow_webapp.services.process_model_service import ProcessModelService
from spiff_workflow_webapp.services.process_instance_service import ProcessInstanceService
from spiff_workflow_webapp.services.spec_file_service import SpecFileService
from spiff_workflow_webapp.models.file import FileSchema, FileType

process_api_blueprint = Blueprint("process_api", __name__)


def add_process_model(body):
    """Add_process_model."""
    spec = ProcessModelInfoSchema().load(body)
    spec_service = ProcessModelService()
    process_group = spec_service.get_process_group(spec.process_group_id)
    spec.process_group = process_group
    workflows = spec_service.cleanup_workflow_spec_display_order(process_group)
    size = len(workflows)
    spec.display_order = size
    spec_service.add_spec(spec)
    return ProcessModelInfoSchema().dump(spec)


def get_file(spec_id, file_name):
    """Get_file."""
    workflow_spec_service = ProcessModelService()
    workflow_spec = workflow_spec_service.get_spec(spec_id)
    files = SpecFileService.get_files(workflow_spec, file_name)
    if len(files) == 0:
        raise ApiError(code='unknown file',
                       message=f'No information exists for file {file_name}'
                               f' it does not exist in workflow {spec_id}.', status_code=404)
    return FileSchema().dump(files[0])


def add_file(spec_id):
    """Add_file."""
    workflow_spec_service = ProcessModelService()
    workflow_spec = workflow_spec_service.get_spec(spec_id)
    file = connexion.request.files['file']
    file = SpecFileService.add_file(workflow_spec, file.filename, file.stream.read())
    if not workflow_spec.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(workflow_spec, file.name)
        workflow_spec_service.update_spec(workflow_spec)
    return FileSchema().dump(file)


def create_process_instance(spec_id):
    """Create_process_instance."""
    workflow_model = ProcessInstanceService.create_process_instance(spec_id, g.user)
    processor = WorkflowProcessor(workflow_model)

    processor.do_engine_steps()
    processor.save()
    ProcessInstanceService.update_task_assignments(processor)

    workflow_api_model = ProcessInstanceService.processor_to_workflow_api(processor)
    return ProcessInstanceApiSchema().dump(workflow_api_model)
