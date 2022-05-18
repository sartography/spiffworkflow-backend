"""Spiff Workflow Connector."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from flask_bpmn.models.db import db
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn.specs.events.event_types import ThrowingEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField
from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter
from SpiffWorkflow.task import Task
from SpiffWorkflow.task import TaskState

from spiff_workflow_webapp.models.process_model import ProcessModel

# from custom_script_engine import CustomScriptEngine

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
    [UserTaskConverter, BusinessRuleTaskConverter]
)
serializer = BpmnWorkflowSerializer(wf_spec_converter)


class Parser(BpmnDmnParser):
    """Parser."""

    OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
    OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)


def parse(process: str, bpmn_files: List[str], dmn_files: List[str]) -> BpmnWorkflow:
    """Parse."""
    parser = Parser()
    parser.add_bpmn_files(bpmn_files)
    if dmn_files:
        parser.add_dmn_files(dmn_files)
    return BpmnWorkflow(parser.get_spec(process))


def format_task(task: Task, include_state: bool = True) -> str:
    """Format_task."""
    if hasattr(task.task_spec, "lane") and task.task_spec.lane is not None:
        lane = f"[{task.task_spec.lane}]"
    else:
        lane = ""
    state = f"[{task.get_state_name()}]" if include_state else ""
    return f"{lane} {task.task_spec.description} ({task.task_spec.name}) {state}"


def complete_user_task(
    task: Task, answer: Optional[Dict[str, str]] = None
) -> Dict[Any, Any]:
    """Complete_user_task."""
    required_user_input_fields = {}
    if task.data is None:
        task.data = {}

    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = {opt.name: opt.id for opt in field.options}
            options = "(" + ", ".join(option_map) + ")"
            if answer is None:
                required_user_input_fields[field.label] = options
            else:
                response = option_map[answer[field.label]]
        elif field.type == "string":
            if answer is None:
                required_user_input_fields[field.label] = "STRING"
            else:
                response = answer[field.label]
        else:
            if answer is None:
                required_user_input_fields[field.label] = "(1..)"
            else:
                if field.type == "long":
                    response = int(answer[field.label])
        if answer:
            task.update_data_var(field.id, response)
    return required_user_input_fields


def get_state(workflow: BpmnWorkflow) -> Dict[str, Union[str, List[str]]]:
    """Print_state."""
    task = workflow.last_task
    return_json = {"last_task": format_task(task)}

    display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
    all_tasks = [
        task
        for task in workflow.get_tasks()
        if isinstance(task.task_spec, display_types)
    ]
    upcoming_tasks = [
        task for task in all_tasks if task.state in [TaskState.READY, TaskState.WAITING]
    ]

    return_json["upcoming_tasks"] = []
    for _idx, task in enumerate(upcoming_tasks):
        return_json["upcoming_tasks"].append(format_task(task))

    return return_json


def run(
    workflow: BpmnWorkflow,
    task_identifier: Optional[str] = None,
    answer: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
    """Run."""
    step = True
    workflow.do_engine_steps()

    while not workflow.is_completed():

        ready_tasks = workflow.get_ready_user_tasks()
        options = {}
        formatted_options = {}

        for idx, task in enumerate(ready_tasks):
            option = format_task(task, False)
            options[str(idx + 1)] = task
            formatted_options[str(idx + 1)] = option

        if task_identifier is None:
            return formatted_options

        next_task = options[task_identifier]
        if isinstance(next_task.task_spec, UserTask):
            if answer is None:
                return complete_user_task(next_task)
            else:
                complete_user_task(next_task, answer)
                next_task.complete()
        elif isinstance(next_task.task_spec, ManualTask):
            next_task.complete()
        else:
            next_task.complete()

        workflow.refresh_waiting_tasks()
        workflow.do_engine_steps()
        tasks_status = {}
        if step:
            tasks_status = get_state(workflow)

        ready_tasks = workflow.get_ready_user_tasks()
        formatted_options = {}
        for idx, task in enumerate(ready_tasks):
            option = format_task(task, False)
            formatted_options[str(idx + 1)] = option

        state = serializer.serialize_json(workflow)
        process_model = ProcessModel.query.filter().first()
        if process_model is None:
            process_model = ProcessModel()
        process_model.bpmn_json = state
        db.session.add(process_model)
        db.session.commit()

        tasks_status["next_activity"] = formatted_options
        return tasks_status
