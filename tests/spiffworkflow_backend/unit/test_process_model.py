"""Process Model."""
from spiffworkflow_backend.models.process_model import ProcessModelInfo


def test_initializes_files_as_empty_array() -> None:
    """Test_initializes_files_as_empty_array."""
    process_model_one = create_test_process_model(id="model_one", display_name="Model One")
    assert process_model_one.files == []
    assert process_model_one.libraries == []


def create_test_process_model(id: str, display_name: str):
    """Create_test_process_model."""
    return ProcessModelInfo(
        id=id,
        display_name=display_name,
        description=display_name,
    )
