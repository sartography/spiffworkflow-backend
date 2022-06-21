"""Process Model."""
from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from flask.app import Flask


def test_there_is_at_least_one_group_after_we_create_one(app: Flask) -> None:
    process_model_service = ProcessModelService()
    process_group = ProcessGroup(id="hey", display_name="sure")
    process_model_service.add_process_group(process_group)
    process_groups = ProcessModelService().get_process_groups()
    assert len(process_groups) > 0
