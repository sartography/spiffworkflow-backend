"""Process_instance_processor."""
from dataclasses import dataclass
from typing import Any
from SpiffWorkflow import Task as SpiffTask  # type: ignore

from spiffworkflow_backend.services.process_instance_processor import CustomBpmnScriptEngine

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
    def run_task(
            cls, task: SpiffTask, script: str, input_context: PythonScriptContext, expected_output_context: PythonScriptContext
    ) -> ScriptUnitTestResult:
        """Run_task."""
        task.data = input_context
        cls._script_engine.execute(task, script)

        result_as_boolean = task.data == expected_output_context
        script_unit_test_result = ScriptUnitTestResult(result=result_as_boolean, context=task.data)
        return script_unit_test_result
