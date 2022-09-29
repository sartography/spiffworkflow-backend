"""Test_process_instance_processor."""
from flask.app import Flask

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)


# it's not totally obvious we want to keep this test/file
def test_script_engine_takes_data_and_returns_expected_results(
    app: Flask,
    with_db_and_bpmn_file_cleanup: None,
) -> None:
    """Test_script_engine_takes_data_and_returns_expected_results."""
    script_engine = ProcessInstanceProcessor._script_engine

    result = script_engine._evaluate("a", {"a": 1})
    assert result == 1
