"""APIs for dealing with process groups, process models, and process instances."""

import connexion
from flask import Blueprint

# from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
# from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
# from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

from flask_bpmn.api.api_error import ApiError

from spiff_workflow_webapp.models.process_model import ProcessModelInfoSchema
from spiff_workflow_webapp.services.process_model_service import ProcessModelService
from spiff_workflow_webapp.services.spec_file_service import SpecFileService
from spiff_workflow_webapp.models.file import FileSchema, FileType
# from spiff_workflow_webapp.spiff_workflow_connector import parse
# from spiff_workflow_webapp.spiff_workflow_connector import run


# wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
#     [UserTaskConverter, BusinessRuleTaskConverter]
# )
# serializer = BpmnWorkflowSerializer(wf_spec_converter)

process_api_blueprint = Blueprint("process_api", __name__)

# ALLOWED_EXTENSIONS = {'bpmn', 'dmn'}
#
#
# @process_api_blueprint.route("/process_models/deploy", methods=["POST"])
# def deploy_model() -> Response:
#     """Deploys the bpmn xml file."""
#     if 'file' not in request.files:
#         raise (
#             ApiError(
#                 code="file_not_given",
#                 message="File was not given.",
#                 status_code=400,
#             )
#         )
#     file = request.files['file']
#     if file.filename == '':
#         raise (
#             ApiError(
#                 code="file_not_given",
#                 message="File was not given.",
#                 status_code=400,
#             )
#         )
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(current_app.config['BPMN_SPEC_ABSOLUTE_DIR'], filename))
#         return Response(
#             json.dumps({"status": "successful", "id": ""}),
#             status=201,
#             mimetype="application/json",
#         )
#     # content = request.json
#     # if content is None:
#     #     return Response(
#     #         json.dumps({"error": "The bpmn xml could not be retrieved from the post body."}),
#     #         status=400,
#     #         mimetype="application/json",
#     #     )
#     #
#
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_workflow_specification(body):
    """Add_workflow_specification."""
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
    workflow_spec_service = ProcessModelService()
    workflow_spec = workflow_spec_service.get_spec(spec_id)
    files = SpecFileService.get_files(workflow_spec, file_name)
    if len(files) == 0:
        raise ApiError(code='unknown file',
                       message=f'No information exists for file {file_name}'
                               f' it does not exist in workflow {spec_id}.', status_code=404)
    return FileSchema().dump(files[0])


def add_file(spec_id):
    workflow_spec_service = ProcessModelService()
    workflow_spec = workflow_spec_service.get_spec(spec_id)
    file = connexion.request.files['file']
    file = SpecFileService.add_file(workflow_spec, file.filename, file.stream.read())
    if not workflow_spec.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(workflow_spec, file.name)
        workflow_spec_service.update_spec(workflow_spec)
    return FileSchema().dump(file)


# def get_workflow_specification(spec_id):
#     """Get_workflow_specification."""
#     spec_service = ProcessModelService()
#     if spec_id is None:
#         raise ApiError('unknown_spec', 'Please provide a valid Workflow Specification ID.')
#     spec = spec_service.get_spec(spec_id)
#
#     if spec is None:
#         raise ApiError('unknown_spec', 'The Workflow Specification "' + spec_id + '" is not recognized.')
#
#     return ProcessModelInfoSchema().dump(spec)
