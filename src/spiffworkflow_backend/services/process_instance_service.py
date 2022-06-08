"""Process_instance_service."""
import time
from datetime import datetime
from typing import List

from flask import current_app
from flask_bpmn.models.db import db
from SpiffWorkflow import NavItem
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.util.deep_merge import DeepMerge

from spiffworkflow_backend.models.process_instance import ProcessInstanceApi
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceStatus
from spiffworkflow_backend.models.task_event import TaskAction
from spiffworkflow_backend.models.task_event import TaskEventModel
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.user_service import UserService


class ProcessInstanceService:
    """ProcessInstanceService."""

    TASK_STATE_LOCKED = "locked"

    @staticmethod
    def create_process_instance(process_model_identifier, user):
        """Get_process_instance_from_spec."""
        process_instance_model = ProcessInstanceModel(
            status=ProcessInstanceStatus.not_started,
            process_initiator=user,
            process_model_identifier=process_model_identifier,
            last_updated=datetime.now(),
            start_in_seconds=time.time(),
        )
        db.session.add(process_instance_model)
        db.session.commit()
        return process_instance_model

    @staticmethod
    def processor_to_process_instance_api(
        processor: ProcessInstanceProcessor, next_task=None
    ):
        """Returns an API model representing the state of the current process_instance.

        If requested, and possible, next_task is set to the current_task.
        """
        navigation = processor.bpmn_process_instance.get_deep_nav_list()
        # ProcessInstanceService.update_navigation(navigation, processor)
        spec_service = ProcessModelService()
        spec = spec_service.get_spec(processor.process_model_identifier)
        process_instance_api = ProcessInstanceApi(
            id=processor.get_process_instance_id(),
            status=processor.get_status(),
            next_task=None,
            # navigation=navigation,
            process_model_identifier=processor.process_model_identifier,
            total_tasks=len(navigation),
            completed_tasks=processor.process_instance_model.completed_tasks,
            last_updated=processor.process_instance_model.last_updated,
            is_review=spec.is_review,
            title=spec.display_name,
        )
        if (
            not next_task
        ):  # The Next Task can be requested to be a certain task, useful for parallel tasks.
            # This may or may not work, sometimes there is no next task to complete.
            next_task = processor.next_task()
        if next_task:
            previous_form_data = ProcessInstanceService.get_previously_submitted_data(
                processor.process_instance_model.id, next_task
            )
            #            DeepMerge.merge(next_task.data, previous_form_data)
            next_task.data = DeepMerge.merge(previous_form_data, next_task.data)

            # process_instance_api.next_task = ProcessInstanceService.spiff_task_to_api_task(next_task, add_docs_and_forms=True)
            # Update the state of the task to locked if the current user does not own the task.
            # user_uids = ProcessInstanceService.get_users_assigned_to_task(processor, next_task)
            # if not UserService.in_list(user_uids, allow_admin_impersonate=True):
            #     process_instance_api.next_task.state = ProcessInstanceService.TASK_STATE_LOCKED

        return process_instance_api

    @staticmethod
    def update_navigation(
        navigation: List[NavItem], processor: ProcessInstanceProcessor
    ):
        """Update_navigation."""
        # Recursive function to walk down through children, and clean up descriptions, and statuses
        for nav_item in navigation:
            spiff_task = processor.bpmn_workflow.get_task(nav_item.task_id)
            if spiff_task:
                nav_item.description = ProcessInstanceService.__calculate_title(
                    spiff_task
                )
                user_uids = ProcessInstanceService.get_users_assigned_to_task(
                    processor, spiff_task
                )
                if (
                    isinstance(spiff_task.task_spec, UserTask)
                    or isinstance(spiff_task.task_spec, ManualTask)
                ) and not UserService.in_list(user_uids, allow_admin_impersonate=True):
                    nav_item.state = ProcessInstanceService.TASK_STATE_LOCKED
            else:
                # Strip off the first word in the description, to meet guidlines for BPMN.
                if nav_item.description:
                    if nav_item.description is not None and " " in nav_item.description:
                        nav_item.description = nav_item.description.partition(" ")[2]

            # Recurse here
            ProcessInstanceService.update_navigation(nav_item.children, processor)

    @staticmethod
    def get_previously_submitted_data(process_instance_id, spiff_task):
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
                return latest_event.form_data
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
