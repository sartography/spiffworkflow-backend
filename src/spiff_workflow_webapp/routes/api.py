"""Api."""
import os

from flask import Blueprint
from flask import request

from ..models.user import User
from spiff_workflow_webapp.spiff_workflow_connector import parse
from spiff_workflow_webapp.spiff_workflow_connector import run

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter
from spiff_workflow_webapp.models.process_model import ProcessModel

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([ UserTaskConverter, BusinessRuleTaskConverter ])
serializer = BpmnWorkflowSerializer(wf_spec_converter)

api = Blueprint("api", __name__)


@api.route("/user/<name>")
def create_user(name):
    """Create_user."""
    user = User.query.filter_by(name=name).first()

    return {"user": user.name}


# @api.route("/run_process", defaults={"answer": None, "task_identifier": None})
# @api.route("/run_process/<task_identifier>", defaults={"answer": None})
# @api.route("/run_process/<task_identifier>/<answer>")
# def run_process(task_identifier, answer):
@api.route("/run_process", methods=['POST'])
def run_process():
    """Run_process."""
    # parser = argparse.ArgumentParser("Simple BPMN runner")
    # parser.add_argument(
    #     "-p", "--process", dest="process", help="The top-level BPMN Process ID"
    # )
    # parser.add_argument(
    #     "-b", "--bpmn", dest="bpmn", nargs="+", help="BPMN files to load"
    # )
    # parser.add_argument("-d", "--dmn", dest="dmn", nargs="*", help="DMN files to load")
    # parser.add_argument(
    #     "-r",
    #     "--restore",
    #     dest="restore",
    #     metavar="FILE",
    #     help="Restore state from %(metavar)s",
    # )
    # parser.add_argument(
    #     "-s",
    #     "--step",
    #     dest="step",
    #     action="store_true",
    #     help="Display state after each step",
    # )
    # args = parser.parse_args()

    content = request.json
    # if 'task_identifier' in content:

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

    # try:
    #     if args.restore is not None:
    #         with open(args.restore) as state:
    #             wf = serializer.deserialize_json(state.read())
    #     else:
    workflow = None
    process_model = ProcessModel.query.filter().first()
    if process_model is None:
        workflow = parse(process, bpmn, dmn)
    else:
        workflow = serializer.deserialize_json(process_model.bpmn_json)
    response = run(workflow, content.get("task_identifier"), content.get("answer"))
    # except Exception:
    #     sys.stderr.write(traceback.format_exc())
    #     sys.exit(1)

    return {"response": response}
