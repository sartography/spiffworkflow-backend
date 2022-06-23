"""Process_instance_service."""
import time
from typing import Any
from typing import Dict
from typing import Optional

from flask import current_app
from flask_bpmn.models.db import db
from SpiffWorkflow.task import Task  # type: ignore
from SpiffWorkflow.util.deep_merge import DeepMerge  # type: ignore

from spiffworkflow_backend.models.process_instance import ProcessInstanceApi
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceStatus
from spiffworkflow_backend.models.task_event import TaskAction
from spiffworkflow_backend.models.task_event import TaskEventModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService


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
        navigation = processor.bpmn_process_instance.get_deep_nav_list()
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
            total_tasks=len(navigation),
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

        if next_task_trying_again:
            previous_form_data = ProcessInstanceService.get_previously_submitted_data(
                processor.process_instance_model.id, next_task_trying_again
            )
            #            DeepMerge.merge(next_task_trying_again.data, previous_form_data)
            next_task_trying_again.data = DeepMerge.merge(
                previous_form_data, next_task_trying_again.data
            )

        return process_instance_api

    @staticmethod
    def get_previously_submitted_data(
        process_instance_id: int, spiff_task: Task
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

    def get_process_instance(self, process_instance_id):
        """Get_process_instance."""
        result = db.session.query(ProcessInstanceModel).filter(ProcessInstanceModel.id == process_instance_id).first()
        return result
