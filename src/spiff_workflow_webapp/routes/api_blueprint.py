"""Api."""
import os
import json

from flask import Blueprint
from flask import request
from flask import Response
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

from spiff_workflow_webapp.models.process_model import ProcessModel
from spiff_workflow_webapp.spiff_workflow_connector import parse
from spiff_workflow_webapp.spiff_workflow_connector import run


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

    homedir = os.environ.get("HOME")
    process = "order_product"
    dmn = [
        f"{homedir}/projects/github/sartography/SpiffExample/bpmn/product_prices.dmn",
        f"{homedir}/projects/github/sartography/SpiffExample/bpmn/shipping_costs.dmn",
    ]
    bpmn = [
        f"{homedir}/projects/github/sartography/SpiffExample/bpmn/multiinstance.bpmn",
        f"{homedir}/projects/github/sartography/SpiffExample/bpmn/call_activity_multi.bpmn",
    ]

    workflow = None
    process_model = ProcessModel.query.filter().first()
    if process_model is None:
        workflow = parse(process, bpmn, dmn)
    else:
        workflow = serializer.deserialize_json(process_model.bpmn_json)

    response = run(workflow, content.get("task_identifier"), content.get("answer"))

    return Response(json.dumps({"response": response}), status=200, mimetype="application/json")
