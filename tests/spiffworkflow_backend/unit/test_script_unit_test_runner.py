"""Test Permissions."""
from flask.app import Flask
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.script_unit_test_runner import PythonScriptContext
from spiffworkflow_backend.services.script_unit_test_runner import ScriptUnitTestRunner


class TestScriptUnitTestRunner(BaseTest):
    """TestScriptUnitTestRunner."""

    def test_takes_data_and_returns_expected_result(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_takes_data_and_returns_expected_result."""
        process_group_id = "test_logging_spiff_logger"
        process_model_id = "simple_script"
        process_model = load_test_spec(
            process_model_id, process_group_id=process_group_id
        )
        process_instance = self.create_process_instance_from_process_model(
            process_model
        )
        processor = ProcessInstanceProcessor(process_instance)
        task = processor.get_task_by_bpmn_identifier("Activity_RunScript")

        input_context: PythonScriptContext = {"a": 1}
        expected_output_context: PythonScriptContext = {"a": 2}
        script = "a = 2"

        unit_test_result = (
            ScriptUnitTestRunner.run_with_task_and_script_and_pre_post_contexts(
                task, script, input_context, expected_output_context
            )
        )

        assert unit_test_result.result
        assert unit_test_result.context == {"a": 2}

        # result = script_engine._evaluate('a', {"a": 1})
        # assert result == 1

        # result = script_engine._execute('a = 1', {})
        # assert result == 1

    def test_fails_when_expected_output_does_not_match_actual_output(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_fails_when_expected_output_does_not_match_actual_output."""
        process_group_id = "test_logging_spiff_logger"
        process_model_id = "simple_script"
        process_model = load_test_spec(
            process_model_id, process_group_id=process_group_id
        )
        process_instance = self.create_process_instance_from_process_model(
            process_model
        )
        processor = ProcessInstanceProcessor(process_instance)
        task = processor.get_task_by_bpmn_identifier("Activity_RunScript")

        input_context: PythonScriptContext = {"a": 1}
        expected_output_context: PythonScriptContext = {"a": 2, "b": 3}
        script = "a = 2"

        unit_test_result = (
            ScriptUnitTestRunner.run_with_task_and_script_and_pre_post_contexts(
                task, script, input_context, expected_output_context
            )
        )

        assert unit_test_result.result is not True
        assert unit_test_result.context == {"a": 2}

    def test_script_with_unit_tests_when_hey_is_passed_in(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_script_with_unit_tests_when_hey_is_passed_in."""
        process_group_id = "script_with_unit_tests"
        process_model_id = "script_with_unit_tests"
        process_model = load_test_spec(
            process_model_id, process_group_id=process_group_id
        )
        process_instance = self.create_process_instance_from_process_model(
            process_model
        )
        processor = ProcessInstanceProcessor(process_instance)
        task = processor.get_task_by_bpmn_identifier("script_with_unit_test_id")

        input_context: PythonScriptContext = {"hey": 1}
        expected_output_context: PythonScriptContext = {"hey": True}

        unit_test_result = ScriptUnitTestRunner.run_test_temp(
            task, input_context, expected_output_context
        )

        assert unit_test_result.result
        assert unit_test_result.context == {"hey": True}

    def test_script_with_unit_tests_when_hey_is_not_passed_in(
        self,
        app: Flask,
        with_db_and_bpmn_file_cleanup: None,
    ) -> None:
        """Test_script_with_unit_tests_when_hey_is_not_passed_in."""
        process_group_id = "script_with_unit_tests"
        process_model_id = "script_with_unit_tests"
        process_model = load_test_spec(
            process_model_id, process_group_id=process_group_id
        )
        process_instance = self.create_process_instance_from_process_model(
            process_model
        )
        processor = ProcessInstanceProcessor(process_instance)
        task = processor.get_task_by_bpmn_identifier("script_with_unit_test_id")

        input_context: PythonScriptContext = {}
        expected_output_context: PythonScriptContext = {"something_else": True}

        unit_test_result = ScriptUnitTestRunner.run_test_temp(
            task, input_context, expected_output_context
        )

        assert unit_test_result.result
        assert unit_test_result.context == expected_output_context
