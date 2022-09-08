"""Process Model."""
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from tests.spiffworkflow_backend.helpers.base_test import BaseTest


class TestProcessModel(BaseTest):
    def test_initializes_files_as_empty_array(self) -> None:
        """Test_initializes_files_as_empty_array."""
        process_model_one = self.create_test_process_model(
            id="model_one", display_name="Model One"
        )
        assert process_model_one.files == []
        assert process_model_one.libraries == []

    def create_test_process_model(self, id: str, display_name: str) -> ProcessModelInfo:
        """Create_test_process_model."""
        return ProcessModelInfo(
            id=id,
            display_name=display_name,
            description=display_name,
        )
