"""Api."""
import json
import os

from flask import Blueprint
from flask import current_app
from flask import request
from flask import Response
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.spiff_workflow_connector import parse
from spiffworkflow_backend.spiff_workflow_connector import run


wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
    [UserTaskConverter, BusinessRuleTaskConverter]
)
serializer = BpmnWorkflowSerializer(wf_spec_converter)

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/run_process", methods=["POST"])
def run_process() -> Response:
    """Run_process."""
    content = request.json
    if content is None:
        return Response(
            json.dumps({"error": "Could not find json request"}),
            status=400,
            mimetype="application/json",
        )

    bpmn_spec_dir = current_app.config["BPMN_SPEC_ABSOLUTE_DIR"]
    process = "order_product"
    dmn = [
        os.path.join(bpmn_spec_dir, "product_prices.dmn"),
        os.path.join(bpmn_spec_dir, "shipping_costs.dmn"),
    ]
    bpmn = [
        os.path.join(bpmn_spec_dir, "multiinstance.bpmn"),
        os.path.join(bpmn_spec_dir, "call_activity_multi.bpmn"),
    ]

    workflow = None
    process_instance = ProcessInstanceModel.query.filter().first()
    if process_instance is None:
        workflow = parse(process, bpmn, dmn)
    else:
        workflow = serializer.deserialize_json(process_instance.bpmn_json)

    response = run(workflow, content.get("task_identifier"), content.get("answer"))

    return Response(
        json.dumps({"response": response}), status=200, mimetype="application/json"
    )