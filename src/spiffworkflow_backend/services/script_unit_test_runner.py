"""Process_instance_processor."""
import json
from dataclasses import dataclass
from typing import Any
from typing import Optional

from SpiffWorkflow import Task as SpiffTask
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException  # type: ignore

from spiffworkflow_backend.services.process_instance_processor import (
    CustomBpmnScriptEngine,
)

PythonScriptContext = dict[str, Any]


@dataclass
class ScriptUnitTestResult:
    """ScriptUnitTestResult."""

    result: bool
    context: Optional[PythonScriptContext] = None
    error: Optional[str] = None
    line_number: Optional[int] = None
    offset: Optional[int] = None


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

        try:
            cls._script_engine.execute(task, script)
        except WorkflowTaskExecException as ex:
            return ScriptUnitTestResult(
                result=False,
                error=f"Failed to execute script: {str(ex)}",
                line_number=ex.line_number,
                offset=ex.offset
            )
        except Exception as ex:
            return ScriptUnitTestResult(
                result=False,
                error=f"Failed to execute script: {str(ex)}",
            )

        result_as_boolean = task.data == expected_output_context
        script_unit_test_result = ScriptUnitTestResult(
            result=result_as_boolean, context=task.data
        )
        return script_unit_test_result

    @classmethod
    def run_test(
        cls,
        task: SpiffTask,
        test_identifier: str,
    ) -> ScriptUnitTestResult:
        """Run_test."""
        # this is totally made up, but hopefully resembles what spiffworkflow ultimately does
        unit_tests = task.task_spec.extensions["unitTests"]
        unit_test = [
            unit_test for unit_test in unit_tests if unit_test["id"] == test_identifier
        ][0]

        input_context = None
        expected_output_context = None
        try:
            input_context = json.loads(unit_test["inputJson"])
        except json.decoder.JSONDecodeError as ex:
            return ScriptUnitTestResult(
                result=False,
                error=f"Failed to parse inputJson: {unit_test['inputJson']}: {str(ex)}",
            )

        try:
            expected_output_context = json.loads(unit_test["expectedOutputJson"])
        except json.decoder.JSONDecodeError as ex:
            return ScriptUnitTestResult(
                result=False,
                error=f"Failed to parse expectedOutputJson: {unit_test['expectedOutputJson']}: {str(ex)}",
            )

        script = task.task_spec.script
        return cls.run_with_task_and_script_and_pre_post_contexts(
            task, script, input_context, expected_output_context
        )
