"""Process_instance_service."""

from datetime import datetime
from flask_bpmn.models.db import db

from SpiffWorkflow.util.deep_merge import DeepMerge

from spiff_workflow_webapp.models.process_instance import ProcessInstanceModel, ProcessInstanceStatus, ProcessInstanceApi
from spiff_workflow_webapp.services.process_instance_processor import ProcessInstanceProcessor
from spiff_workflow_webapp.services.process_model_service import ProcessModelService


class ProcessInstanceService():
    """ProcessInstanceService."""

    @staticmethod
    def create_process_instance(process_model_identifier, user):
        """Get_process_instance_from_spec."""
        process_instance_model = ProcessInstanceModel(status=ProcessInstanceStatus.not_started,
                                                      process_initiator=user,
                                                      process_model_identifier=process_model_identifier,
                                                      last_updated=datetime.now())
        db.session.add(process_instance_model)
        db.session.commit()
        return process_instance_model

    @staticmethod
    def processor_to_process_instance_api(processor: ProcessInstanceProcessor, next_task=None):
        """Returns an API model representing the state of the current process_instance, if requested, and
        possible, next_task is set to the current_task."""
        navigation = processor.bpmn_process_instance.get_deep_nav_list()
        ProcessInstanceService.update_navigation(navigation, processor)
        spec_service = ProcessModelService()
        spec = spec_service.get_spec(processor.process_model_id)
        process_instance_api = ProcessInstanceApi(
            id=processor.get_process_instance_id(),
            status=processor.get_status(),
            next_task=None,
            navigation=navigation,
            process_model_identifier=processor.process_model_identifier,
            total_tasks=len(navigation),
            completed_tasks=processor.process_instance_model.completed_tasks,
            last_updated=processor.process_instance_model.last_updated,
            is_review=spec.is_review,
            title=spec.display_name,
            study_id=processor.process_instance_model.study_id or None,
            state=processor.process_instance_model.state
        )
        if not next_task:  # The Next Task can be requested to be a certain task, useful for parallel tasks.
            # This may or may not work, sometimes there is no next task to complete.
            next_task = processor.next_task()
        if next_task:
            previous_form_data = ProcessInstanceService.get_previously_submitted_data(
                processor.process_instance_model.id, next_task)
            #            DeepMerge.merge(next_task.data, previous_form_data)
            next_task.data = DeepMerge.merge(previous_form_data, next_task.data)

            # process_instance_api.next_task = ProcessInstanceService.spiff_task_to_api_task(next_task, add_docs_and_forms=True)
            # Update the state of the task to locked if the current user does not own the task.
            # user_uids = ProcessInstanceService.get_users_assigned_to_task(processor, next_task)
            # if not UserService.in_list(user_uids, allow_admin_impersonate=True):
            #     process_instance_api.next_task.state = ProcessInstanceService.TASK_STATE_LOCKED

        return process_instance_api
