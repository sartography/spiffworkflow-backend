"""Process_instance_processor."""
from dataclasses import dataclass
from typing import Any

from SpiffWorkflow import Task as SpiffTask  # type: ignore

from spiffworkflow_backend.services.process_instance_processor import (
    CustomBpmnScriptEngine,
)

PythonScriptContext = dict[str, Any]


@dataclass
class ScriptUnitTestResult:
    """ScriptUnitTestResult."""

    result: bool
    context: PythonScriptContext


class ScriptUnitTestRunner:
    """ScriptUnitTestRunner."""

    _script_engine = CustomBpmnScriptEngine()

    @classmethod
    def run_with_task_and_script_and_pre_post_contexts(
        cls,
        task: SpiffTask,
        script: str,
        input_context: PythonScriptContext,
        expected_output_context: PythonScriptContext,
    ) -> ScriptUnitTestResult:
        """Run_task."""
        task.data = input_context
        cls._script_engine.execute(task, script)

        result_as_boolean = task.data == expected_output_context
        script_unit_test_result = ScriptUnitTestResult(
            result=result_as_boolean, context=task.data
        )
        return script_unit_test_result

    # run_test_temp is just so we can write tests against this class until run_test (below) is implementable
    # when spiffworkflow starts exposing the unit tests of each script task in the spiff xml extensions
    @classmethod
    def run_test_temp(
        cls,
        task: SpiffTask,
        input_context: PythonScriptContext,
        expected_output_context: PythonScriptContext,
    ) -> ScriptUnitTestResult:
        """Run_test_temp."""
        script = task.task_spec.script
        return cls.run_with_task_and_script_and_pre_post_contexts(
            task, script, input_context, expected_output_context
        )

    @classmethod
    def run_test(
        cls,
        task: SpiffTask,
        test_identifier: str,
    ) -> ScriptUnitTestResult:
        """Run_test."""
        # this is totally made up, but hopefully resembles what spiffworkflow ultimately does
        unit_tests = task.task_spec.extensions["unit_tests"]
        unit_test = [
            unit_test
            for unit_test in unit_tests
            if unit_test["test_identifier"] == test_identifier
        ][0]

        input_context = unit_test["input_json"]
        expected_output_context = unit_test["expected_output_json"]
        script = task.task_spec.script
        return cls.run_with_task_and_script_and_pre_post_contexts(
            task, script, input_context, expected_output_context
        )
