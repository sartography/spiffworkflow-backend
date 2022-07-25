"""Process_instance_service."""
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from flask import current_app
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db
from SpiffWorkflow.bpmn.specs.events import EndEvent  # type: ignore
from SpiffWorkflow.bpmn.specs.events import StartEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask  # type: ignore
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask  # type: ignore
from SpiffWorkflow.bpmn.specs.UserTask import UserTask  # type: ignore
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField  # type: ignore
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask  # type: ignore
from SpiffWorkflow.specs import CancelTask  # type: ignore
from SpiffWorkflow.specs import StartTask
from SpiffWorkflow.task import Task as SpiffTask  # type: ignore
from SpiffWorkflow.util.deep_merge import DeepMerge  # type: ignore

from spiffworkflow_backend.models.process_instance import ProcessInstanceApi
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceStatus
from spiffworkflow_backend.models.task import MultiInstanceType
from spiffworkflow_backend.models.task import Task
from spiffworkflow_backend.models.task_event import TaskAction
from spiffworkflow_backend.models.task_event import TaskEventModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService

# from SpiffWorkflow.task import TaskState  # type: ignore


class ProcessInstanceService:
    """ProcessInstanceService."""

    TASK_STATE_LOCKED = "locked"

    @staticmethod
    def create_process_instance(
        process_model_identifier: str,
        user: UserModel,
        process_group_identifier: Optional[str] = None,
    ) -> ProcessInstanceModel:
        """Get_process_instance_from_spec."""
        process_instance_model = ProcessInstanceModel(
            status=ProcessInstanceStatus.not_started.value,
            process_initiator=user,
            process_model_identifier=process_model_identifier,
            process_group_identifier=process_group_identifier,
            start_in_seconds=round(time.time()),
        )
        db.session.add(process_instance_model)
        db.session.commit()
        return process_instance_model

    @staticmethod
    def processor_to_process_instance_api(
        processor: ProcessInstanceProcessor, next_task: None = None
    ) -> ProcessInstanceApi:
        """Returns an API model representing the state of the current process_instance.

        If requested, and possible, next_task is set to the current_task.
        """
        # navigation = processor.bpmn_process_instance.get_deep_nav_list()
        # ProcessInstanceService.update_navigation(navigation, processor)
        process_model_service = ProcessModelService()
        process_model = process_model_service.get_process_model(
            processor.process_model_identifier
        )
        is_review_value = process_model.is_review if process_model else False
        title_value = process_model.display_name if process_model else ""
        process_instance_api = ProcessInstanceApi(
            id=processor.get_process_instance_id(),
            status=processor.get_status(),
            next_task=None,
            # navigation=navigation,
            process_model_identifier=processor.process_model_identifier,
            process_group_identifier=processor.process_group_identifier,
            # total_tasks=len(navigation),
            completed_tasks=processor.process_instance_model.completed_tasks,
            updated_at_in_seconds=processor.process_instance_model.updated_at_in_seconds,
            is_review=is_review_value,
            title=title_value,
        )
        next_task_trying_again = next_task
        if (
            not next_task
        ):  # The Next Task can be requested to be a certain task, useful for parallel tasks.
            # This may or may not work, sometimes there is no next task to complete.
            next_task_trying_again = processor.next_task()

        if next_task_trying_again is not None:
            previous_form_data = ProcessInstanceService.get_previously_submitted_data(
                processor.process_instance_model.id, next_task_trying_again
            )
            #            DeepMerge.merge(next_task_trying_again.data, previous_form_data)
            next_task_trying_again.data = DeepMerge.merge(
                previous_form_data, next_task_trying_again.data
            )

            process_instance_api.next_task = (
                ProcessInstanceService.spiff_task_to_api_task(
                    next_task_trying_again, add_docs_and_forms=True
                )
            )
            # TODO: Hack for now, until we decide how to implment forms
            process_instance_api.next_task.form = None

            # Update the state of the task to locked if the current user does not own the task.
            # user_uids = WorkflowService.get_users_assigned_to_task(processor, next_task)
            # if not UserService.in_list(user_uids, allow_admin_impersonate=True):
            #     workflow_api.next_task.state = WorkflowService.TASK_STATE_LOCKED

        return process_instance_api

    @staticmethod
    def get_previously_submitted_data(
        process_instance_id: int, spiff_task: SpiffTask
    ) -> Dict[Any, Any]:
        """If the user has completed this task previously, find the form data for the last submission."""
        query = (
            db.session.query(TaskEventModel)
            .filter_by(process_instance_id=process_instance_id)
            .filter_by(task_name=spiff_task.task_spec.name)
            .filter_by(action=TaskAction.COMPLETE.value)
        )

        if (
            hasattr(spiff_task, "internal_data")
            and "runtimes" in spiff_task.internal_data
        ):
            query = query.filter_by(mi_index=spiff_task.internal_data["runtimes"])

        latest_event = query.order_by(TaskEventModel.date.desc()).first()
        if latest_event:
            if latest_event.form_data is not None:
                return latest_event.form_data  # type: ignore
            else:
                missing_form_error = (
                    f"We have lost data for workflow {process_instance_id}, "
                    f"task {spiff_task.task_spec.name}, it is not in the task event model, "
                    f"and it should be."
                )
                current_app.logger.error(
                    "missing_form_data", missing_form_error, exc_info=True
                )
                return {}
        else:
            return {}

    def get_process_instance(self, process_instance_id: int) -> Any:
        """Get_process_instance."""
        result = (
            db.session.query(ProcessInstanceModel)
            .filter(ProcessInstanceModel.id == process_instance_id)
            .first()
        )
        return result

    @staticmethod
    def update_task_assignments(processor: ProcessInstanceProcessor) -> None:
        """For every upcoming user task, log a task action that connects the assigned user(s) to that task.

        All existing assignment actions for this workflow are removed from the database,
        so that only the current valid actions are available. update_task_assignments
        should be called whenever progress is made on a workflow.
        """
        db.session.query(TaskEventModel).filter(
            TaskEventModel.process_instance_id == processor.process_instance_model.id
        ).filter(TaskEventModel.action == TaskAction.ASSIGNMENT.value).delete()
        db.session.commit()

        tasks = processor.get_current_user_tasks()
        for task in tasks:
            user_ids = ProcessInstanceService.get_users_assigned_to_task(
                processor, task
            )

            for user_id in user_ids:
                ProcessInstanceService().log_task_action(
                    user_id, processor, task, TaskAction.ASSIGNMENT.value
                )

    @staticmethod
    def get_users_assigned_to_task(
        processor: ProcessInstanceProcessor, spiff_task: SpiffTask
    ) -> List[int]:
        """Get_users_assigned_to_task."""
        if processor.process_instance_model.process_initiator_id is None:
            raise ApiError.from_task(
                code="invalid_workflow",
                message="A process instance must have a user_id.",
                task=spiff_task,
            )
        # # Standalone workflow - we only care about the current user
        # elif processor.workflow_model.study_id is None and processor.workflow_model.user_id is not None:
        #     return [processor.workflow_model.user_id]

        # Workflow associated with a study - get all the users
        else:
            if (
                not hasattr(spiff_task.task_spec, "lane")
                or spiff_task.task_spec.lane is None
            ):
                current_user = spiff_task.data["current_user"]
                return [
                    current_user["id"],
                ]
                # return [processor.process_instance_model.process_initiator_id]

            if spiff_task.task_spec.lane not in spiff_task.data:
                return []  # No users are assignable to the task at this moment
            lane_users = spiff_task.data[spiff_task.task_spec.lane]
            if not isinstance(lane_users, list):
                lane_users = [lane_users]

            lane_uids = []
            for user in lane_users:
                if isinstance(user, dict):
                    if user.get("value"):
                        lane_uids.append(user["value"])
                    else:
                        raise ApiError.from_task(
                            code="task_lane_user_error",
                            message="Spiff Task %s lane user dict must have a key called 'value' with the user's uid in it."
                            % spiff_task.task_spec.name,
                            task=spiff_task,
                        )
                elif isinstance(user, str):
                    lane_uids.append(user)
                else:
                    raise ApiError.from_task(
                        code="task_lane_user_error",
                        message="Spiff Task %s lane user is not a string or dict"
                        % spiff_task.task_spec.name,
                        task=spiff_task,
                    )

            return lane_uids

    # @staticmethod
    # def get_task_type(spiff_task: SpiffTask):
    #     """Get_task_type."""
    #     task_type = spiff_task.task_spec.__class__.__name__
    #
    #     task_types = [
    #         UserTask,
    #         ManualTask,
    #         BusinessRuleTask,
    #         CancelTask,
    #         ScriptTask,
    #         StartTask,
    #         EndEvent,
    #         StartEvent,
    #     ]
    #
    #     for t in task_types:
    #         if isinstance(spiff_task.task_spec, t):
    #             task_type = t.__name__
    #             break
    #         else:
    #             task_type = "NoneTask"
    #     return task_type

    @staticmethod
    def complete_form_task(
        processor: ProcessInstanceProcessor,
        spiff_task: SpiffTask,
        data: dict[str, Any],
        user: UserModel,
    ) -> None:
        """All the things that need to happen when we complete a form.

        Abstracted here because we need to do it multiple times when completing all tasks in
        a multi-instance task.
        """
        spiff_task.update_data(data)
        # ProcessInstanceService.post_process_form(spiff_task)  # some properties may update the data store.
        processor.complete_task(spiff_task)
        # Log the action before doing the engine steps, as doing so could effect the state of the task
        # the workflow could wrap around in the ngine steps, and the task could jump from being completed to
        # another state.  What we are logging here is the completion.
        ProcessInstanceService.log_task_action(
            user.id, processor, spiff_task, TaskAction.COMPLETE.value
        )
        processor.do_engine_steps()
        processor.save()

    @staticmethod
    def log_task_action(
        user_id: int,
        processor: ProcessInstanceProcessor,
        spiff_task: SpiffTask,
        action: str,
    ) -> None:
        """Log_task_action."""
        task = ProcessInstanceService.spiff_task_to_api_task(spiff_task)
        form_data = ProcessInstanceService.extract_form_data(
            spiff_task.data, spiff_task
        )
        multi_instance_type_value = ""
        if task.multi_instance_type:
            multi_instance_type_value = task.multi_instance_type.value

        task_event = TaskEventModel(
            # study_id=processor.workflow_model.study_id,
            user_id=user_id,
            process_instance_id=processor.process_instance_model.id,
            # workflow_spec_id=processor.workflow_model.workflow_spec_id,
            action=action,
            task_id=str(task.id),
            task_name=task.name,
            task_title=task.title,
            task_type=str(task.type),
            task_state=task.state,
            task_lane=task.lane,
            form_data=form_data,
            mi_type=multi_instance_type_value,  # Some tasks have a repeat behavior.
            mi_count=task.multi_instance_count,  # This is the number of times the task could repeat.
            mi_index=task.multi_instance_index,  # And the index of the currently repeating task.
            process_name=task.process_name,
            # date=datetime.utcnow(), <=== For future reference, NEVER do this. Let the database set the time.
        )
        db.session.add(task_event)
        db.session.commit()

    @staticmethod
    def extract_form_data(latest_data: dict, task: SpiffTask) -> dict:
        """Extracts data from the latest_data that is directly related to the form that is being submitted."""
        data = {}

        if hasattr(task.task_spec, "form"):
            for field in task.task_spec.form.fields:
                if field.has_property(Task.FIELD_PROP_REPEAT):
                    group = field.get_property(Task.FIELD_PROP_REPEAT)
                    if group in latest_data:
                        data[group] = latest_data[group]
                else:
                    value = ProcessInstanceService.get_dot_value(field.id, latest_data)
                    if value is not None:
                        ProcessInstanceService.set_dot_value(field.id, value, data)
        return data

    @staticmethod
    def get_dot_value(path: str, source: dict) -> Any:
        """Get_dot_value."""
        # Given a path in dot notation, uas as 'fruit.type' tries to find that value in
        # the source, but looking deep in the dictionary.
        paths = path.split(".")  # [a,b,c]
        s = source
        index = 0
        for p in paths:
            index += 1
            if isinstance(s, dict) and p in s:
                if index == len(paths):
                    return s[p]
                else:
                    s = s[p]
        if path in source:
            return source[path]
        return None

    @staticmethod
    def set_dot_value(path: str, value: Any, target: dict) -> dict:
        """Set_dot_value."""
        # Given a path in dot notation, such as "fruit.type", and a value "apple", will
        # set the value in the target dictionary, as target["fruit"]["type"]="apple"
        destination = target
        paths = path.split(".")  # [a,b,c]
        index = 0
        for p in paths:
            index += 1
            if p not in destination:
                if index == len(paths):
                    destination[p] = value
                else:
                    destination[p] = {}
            destination = destination[p]
        return target

    @staticmethod
    def spiff_task_to_api_task(
        spiff_task: SpiffTask, add_docs_and_forms: bool = False
    ) -> Task:
        """Spiff_task_to_api_task."""
        task_type = spiff_task.task_spec.__class__.__name__

        task_types = [
            UserTask,
            ManualTask,
            BusinessRuleTask,
            CancelTask,
            ScriptTask,
            StartTask,
            EndEvent,
            StartEvent,
        ]

        for t in task_types:
            if isinstance(spiff_task.task_spec, t):
                task_type = t.__name__
                break
            else:
                task_type = "NoneTask"

        info = spiff_task.task_info()
        if info["is_looping"]:
            mi_type = MultiInstanceType.looping
        elif info["is_sequential_mi"]:
            mi_type = MultiInstanceType.sequential
        elif info["is_parallel_mi"]:
            mi_type = MultiInstanceType.parallel
        else:
            mi_type = MultiInstanceType.none

        props = {}
        if hasattr(spiff_task.task_spec, "extensions"):
            for key, val in spiff_task.task_spec.extensions.items():
                props[key] = val

        if hasattr(spiff_task.task_spec, "lane"):
            lane = spiff_task.task_spec.lane
        else:
            lane = None

        task = Task(
            spiff_task.id,
            spiff_task.task_spec.name,
            spiff_task.task_spec.description,
            task_type,
            spiff_task.get_state_name(),
            lane=lane,
            multi_instance_type=mi_type,
            multi_instance_count=info["mi_count"],
            multi_instance_index=info["mi_index"],
            process_name=spiff_task.task_spec._wf_spec.description,
            properties=props,
        )

        # # Only process the form and documentation if requested.
        # # The task should be in a completed or a ready state, and should
        # # not be a previously completed MI Task.
        # if add_docs_and_forms:
        #     task.data = spiff_task.data
        #     if (
        #         hasattr(spiff_task.task_spec, "form")
        #         and spiff_task.task_spec.form is not None
        #     ):
        #         task.form = spiff_task.task_spec.form
        #         for i, field in enumerate(task.form.fields):
        #             task.form.fields[i] = ProcessInstanceService.process_options(
        #                 spiff_task, field
        #             )
        #             # If there is a default value, set it.
        #             # if field.id not in task.data and ProcessInstanceService.get_default_value(field, spiff_task) is not None:
        #             #    task.data[field.id] = ProcessInstanceService.get_default_value(field, spiff_task)
        #     # task.documentation = ProcessInstanceService._process_documentation(spiff_task)
        #     task.documentation = (
        #         spiff_task.task_spec.documentation
        #         if hasattr(spiff_task.task_spec, "documentation")
        #         else None
        #     )

        # All ready tasks should have a valid name, and this can be computed for
        # some tasks, particularly multi-instance tasks that all have the same spec
        # but need different labels.
        # if spiff_task.state == TaskState.READY:
        #     task.properties = ProcessInstanceService._process_properties(spiff_task, props)
        #
        # task.title = ProcessInstanceService.__calculate_title(spiff_task)

        # if task.properties and "clear_data" in task.properties:
        #     if task.form and task.properties["clear_data"] == "True":
        #         for i in range(len(task.form.fields)):
        #             task.data.pop(task.form.fields[i].id, None)

        # # Pass help text through the Jinja parser
        # if task.form and task.form.fields:
        #     for field in task.form.fields:
        #         if field.properties:
        #             for field_property in field.properties:
        #                 if field_property.id == "help":
        #                     jinja_text = JinjaService().get_content(
        #                         field_property.value, task.data
        #                     )
        #                     field_property.value = jinja_text

        return task

    # @staticmethod
    # def _process_properties(spiff_task, props):
    #     """Runs all the property values through the Jinja2 processor to inject data."""
    #     for k, v in props.items():
    #         try:
    #             props[k] = JinjaService.get_content(v, spiff_task.data)
    #         except jinja2.exceptions.TemplateError as ue:
    #             app.logger.error(
    #                 f"Failed to process task property {str(ue)}", exc_info=True
    #             )
    #     return props

    @staticmethod
    def process_options(spiff_task: SpiffTask, field: EnumFormField) -> EnumFormField:
        """Process_options."""
        if field.type != Task.FIELD_TYPE_ENUM:
            return field

        if hasattr(field, "options") and len(field.options) > 1:
            return field
        elif not (
            field.has_property(Task.FIELD_PROP_VALUE_COLUMN)
            or field.has_property(Task.FIELD_PROP_LABEL_COLUMN)
        ):
            raise ApiError.from_task(
                "invalid_enum",
                f"For enumerations, you must include options, or a way to generate options from"
                f" a spreadsheet or data set. Please set either a spreadsheet name or data name,"
                f" along with the value and label columns to use from these sources.  Valid params"
                f" include: "
                f"{Task.FIELD_PROP_SPREADSHEET_NAME}, "
                f"{Task.FIELD_PROP_DATA_NAME}, "
                f"{Task.FIELD_PROP_VALUE_COLUMN}, "
                f"{Task.FIELD_PROP_LABEL_COLUMN}",
                task=spiff_task,
            )

        if field.has_property(Task.FIELD_PROP_SPREADSHEET_NAME):
            # lookup_model = LookupService.get_lookup_model(spiff_task, field)
            # data = (
            #     db.session.query(LookupDataModel)
            #     .filter(LookupDataModel.lookup_file_model == lookup_model)
            #     .all()
            # )
            # for d in data:
            #     field.add_option(d.value, d.label)
            ...
        elif field.has_property(Task.FIELD_PROP_DATA_NAME):
            field.options = ProcessInstanceService.get_options_from_task_data(
                spiff_task, field
            )

        return field

    @staticmethod
    def get_options_from_task_data(spiff_task: SpiffTask, field: EnumFormField) -> List:
        """Get_options_from_task_data."""
        prop = field.get_property(Task.FIELD_PROP_DATA_NAME)
        if prop not in spiff_task.data:
            raise ApiError.from_task(
                "invalid_enum",
                f"For enumerations based on task data, task data must have "
                f"a property called {prop}",
                task=spiff_task,
            )
        # Get the enum options from the task data
        data_model = spiff_task.data[prop]
        value_column = field.get_property(Task.FIELD_PROP_VALUE_COLUMN)
        label_column = field.get_property(Task.FIELD_PROP_LABEL_COLUMN)
        items = data_model.items() if isinstance(data_model, dict) else data_model
        options: List[Any] = []
        for item in items:
            if value_column not in item:
                raise ApiError.from_task(
                    "invalid_enum",
                    f"The value column '{value_column}' does not exist for item {item}",
                    task=spiff_task,
                )
            if label_column not in item:
                raise ApiError.from_task(
                    "invalid_enum",
                    f"The label column '{label_column}' does not exist for item {item}",
                    task=spiff_task,
                )

            # options.append(
            #     Box(
            #         {"id": item[value_column], "name": item[label_column], "data": item}
            #     )
            # )
        return options

    # @staticmethod
    # def _process_documentation(spiff_task):
    #     """Runs the given documentation string through the Jinja2 processor to inject data
    #     create loops, etc...  - If a markdown file exists with the same name as the task id,
    #     it will use that file instead of the documentation."""
    #     documentation = (
    #         spiff_task.task_spec.documentation
    #         if hasattr(spiff_task.task_spec, "documentation")
    #         else ""
    #     )
    #
    #     try:
    #         doc_file_name = spiff_task.task_spec.name + ".md"
    #
    #         workflow_id = WorkflowService.workflow_id_from_spiff_task(spiff_task)
    #         workflow = (
    #             db.session.query(WorkflowModel)
    #             .filter(WorkflowModel.id == workflow_id)
    #             .first()
    #         )
    #         spec_service = WorkflowSpecService()
    #         data = SpecFileService.get_data(
    #             spec_service.get_spec(workflow.workflow_spec_id), doc_file_name
    #         )
    #         raw_doc = data.decode("utf-8")
    #     except ApiError:
    #         raw_doc = documentation
    #
    #     if not raw_doc:
    #         return ""
    #
    #     try:
    #         return JinjaService.get_content(raw_doc, spiff_task.data)
    #     except jinja2.exceptions.TemplateSyntaxError as tse:
    #         lines = tse.source.splitlines()
    #         error_line = ""
    #         if len(lines) >= tse.lineno - 1:
    #             error_line = tse.source.splitlines()[tse.lineno - 1]
    #         raise ApiError.from_task(
    #             code="template_error",
    #             message="Jinja Template Error:  %s" % str(tse),
    #             task=spiff_task,
    #             line_number=tse.lineno,
    #             error_line=error_line,
    #         )
    #     except jinja2.exceptions.TemplateError as te:
    #         # Figure out the line number in the template that caused the error.
    #         cl, exc, tb = sys.exc_info()
    #         line_number = None
    #         error_line = None
    #         for frame_summary in traceback.extract_tb(tb):
    #             if frame_summary.filename == "<template>":
    #                 line_number = frame_summary.lineno
    #                 lines = documentation.splitlines()
    #                 error_line = ""
    #                 if len(lines) > line_number:
    #                     error_line = lines[line_number - 1]
    #         raise ApiError.from_task(
    #             code="template_error",
    #             message="Jinja Template Error: %s" % str(te),
    #             task=spiff_task,
    #             line_number=line_number,
    #             error_line=error_line,
    #         )
    #     except TypeError as te:
    #         raise ApiError.from_task(
    #             code="template_error",
    #             message="Jinja Template Error: %s" % str(te),
    #             task=spiff_task,
    #         ) from te
    #     except Exception as e:
    #         # app.logger.error(str(e), exc_info=True)
    #         ...
