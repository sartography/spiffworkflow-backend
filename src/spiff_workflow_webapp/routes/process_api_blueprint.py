"""APIs for dealing with process groups, process models, and process instances."""

import os
import json
from flask import Blueprint
from flask import current_app
from flask import request
from flask import Response
from werkzeug.utils import secure_filename

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

from flask_bpmn.api.api_error import ApiError

# from spiff_workflow_webapp.models.process_instance import ProcessInstanceModel
# from spiff_workflow_webapp.spiff_workflow_connector import parse
# from spiff_workflow_webapp.spiff_workflow_connector import run


wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
    [UserTaskConverter, BusinessRuleTaskConverter]
)
serializer = BpmnWorkflowSerializer(wf_spec_converter)

process_api_blueprint = Blueprint("process_api", __name__)

ALLOWED_EXTENSIONS = {'bpmn', 'dmn'}


@process_api_blueprint.route("/process_models/deploy", methods=["POST"])
def deploy_model() -> Response:
    """Deploys the bpmn xml file."""
    if 'file' not in request.files:
        raise (
            ApiError(
                code="file_not_given",
                message="File was not given.",
                status_code=400,
            )
        )
    file = request.files['file']
    if file.filename == '':
        raise (
            ApiError(
                code="file_not_given",
                message="File was not given.",
                status_code=400,
            )
        )
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['BPMN_SPEC_ABSOLUTE_DIR'], filename))
        return Response(
            json.dumps({"status": "successful", "id": ""}),
            status=201,
            mimetype="application/json",
        )
    # content = request.json
    # if content is None:
    #     return Response(
    #         json.dumps({"error": "The bpmn xml could not be retrieved from the post body."}),
    #         status=400,
    #         mimetype="application/json",
    #     )
    #


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
