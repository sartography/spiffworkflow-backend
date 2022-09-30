"""Test_process_instance_processor."""
from flask.app import Flask
from SpiffWorkflow import TaskState  # type: ignore
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)


class TestProcessInstanceProcessor(BaseTest):
    """TestProcessInstanceProcessor."""

    # it's not totally obvious we want to keep this test/file
    def test_script_engine_takes_data_and_returns_expected_results(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_script_engine_takes_data_and_returns_expected_results."""
        script_engine = ProcessInstanceProcessor._script_engine

        result = script_engine._evaluate("a", {"a": 1})
        assert result == 1

    # FIXME: print statements for debugging
    def test_get_bpmn_process_instance_from_process_model_can_access_tasks_from_subprocesses(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_get_bpmn_process_instance_from_process_model_can_access_tasks_from_subprocesses."""
        app.config["THREAD_LOCAL_DATA"].process_instance_id = None
        process_model = load_test_spec(
            "hello_world",
            process_model_source_directory="hello_world",
        )

        # BpmnWorkflow instance
        bpmn_process_instance = (
            ProcessInstanceProcessor.get_bpmn_process_instance_from_process_model(
                process_group_identifier="test_process_group_id",
                process_model_identifier="hello_world",
            )
        )

        tasks = bpmn_process_instance.get_tasks(TaskState.ANY_MASK)
        subprocess_specs = bpmn_process_instance.subprocess_specs
        task_ids = [t.task_spec.name for t in tasks]
        print("\nWITHOUT INSTANCE")
        print(f"task_ids: {task_ids}\n")
        print(f"task_ids length: {len(task_ids)}\n")
        print(f"subprocess_specs: {subprocess_specs}")

        user = self.find_or_create_user()

        process_instance = ProcessInstanceService.create_process_instance(
            process_model.id,
            user,
            process_group_identifier=process_model.process_group_id,
        )

        processor = ProcessInstanceProcessor(process_instance)
        processor.do_engine_steps()
        processor.save()

        print("\nWITH INSTANCE")
        bpmn_process_instance = processor.bpmn_process_instance
        tasks = bpmn_process_instance.get_tasks(TaskState.ANY_MASK)
        subprocess_specs = bpmn_process_instance.subprocess_specs
        task_ids = [t.task_spec.name for t in tasks]
        print(f"task_ids: {task_ids}\n")
        print(f"subprocess_specs: {subprocess_specs}")
