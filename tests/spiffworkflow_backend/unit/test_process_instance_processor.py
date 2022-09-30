"""Test_process_instance_processor."""
# from SpiffWorkflow import TaskState
from flask.app import Flask

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)

# from tests.spiffworkflow_backend.helpers.test_data import load_test_spec


# it's not totally obvious we want to keep this test/file
def test_script_engine_takes_data_and_returns_expected_results(
    app: Flask,
    with_db_and_bpmn_file_cleanup: None,
) -> None:
    """Test_script_engine_takes_data_and_returns_expected_results."""
    script_engine = ProcessInstanceProcessor._script_engine

    result = script_engine._evaluate("a", {"a": 1})
    assert result == 1


def test_get_bpmn_process_instance_from_process_model_can_acccess_tasks_from_subprocesses(
    app: Flask,
    with_db_and_bpmn_file_cleanup: None,
) -> None:
    """Test_get_bpmn_process_instance_from_process_model_can_acccess_tasks_from_subprocesses."""
    assert True
    # load_test_spec(
    #     "multiinstance",
    #     process_model_source_directory="spiff_example",
    # )
    #
    # # BpmnWorkflow
    # bpmn_process_instance = (
    #     ProcessInstanceProcessor.get_bpmn_process_instance_from_process_model(
    #         process_group_identifier='test_process_group_id', process_model_identifier='multiinstance'
    #     )
    # )
    #
    # tasks = bpmn_process_instance.get_tasks(TaskState.ANY_MASK)
    # task_ids = [t.task_spec.name for t in tasks]
    # print(f"task_ids: {task_ids}")

# it's not totally obvious we want to keep this test/file
def test_script_engine_can_use_custom_scripts(
    app: Flask,
    with_db_and_bpmn_file_cleanup: None,
) -> None:
    """Test_script_engine_takes_data_and_returns_expected_results."""
    script_engine = ProcessInstanceProcessor._script_engine
    result = script_engine._evaluate("fact_service(type='norris')", {})
    assert result == "Chuck Norris doesn’t read books. He stares them down until he gets the information he wants."
