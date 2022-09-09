"""Process Model."""
from flask.app import Flask
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)


class TestProcessModel(BaseTest):
    """TestProcessModel."""

    def test_initializes_files_as_empty_array(self) -> None:
        """Test_initializes_files_as_empty_array."""
        process_model_one = self.create_test_process_model(
            id="model_one", display_name="Model One"
        )
        assert process_model_one.files == []
        assert process_model_one.libraries == []

    def test_can_run_process_model_with_call_activities(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_can_run_process_model_with_call_activities."""
        process_model = load_test_spec(
            "call_activity_nested",
            process_model_source_directory="call_activity_nested",
            bpmn_file_name="call_activity_nested",
        )

        bpmn_file_names = [
            "call_activity_level_2b",
            "call_activity_level_2",
            "call_activity_level_3",
        ]
        for bpmn_file_name in bpmn_file_names:
            load_test_spec(
                bpmn_file_name,
                process_model_source_directory="call_activity_nested",
                bpmn_file_name=bpmn_file_name,
            )
        process_instance = self.create_process_instance_from_process_model(
            process_model
        )
        processor = ProcessInstanceProcessor(process_instance)
        processor.do_engine_steps()

    def create_test_process_model(self, id: str, display_name: str) -> ProcessModelInfo:
        """Create_test_process_model."""
        return ProcessModelInfo(
            id=id,
            display_name=display_name,
            description=display_name,
        )
