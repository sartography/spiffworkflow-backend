"""Test_process_instance_processor."""
from flask.app import Flask
from tests.spiffworkflow_backend.helpers.base_test import BaseTest

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
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
