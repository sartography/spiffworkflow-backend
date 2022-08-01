"""test_message_service."""
from spiffworkflow_backend.services.message_model import MessageModel
from spiffworkflow_backend.services.message_instance import MessageInstanceModel
from tests.spiffworkflow_backend.helpers.test_data import create_process_instance_from_process_model


def test_can_send_message_to_waiting_message() -> None:
    """Test_can_send_message_to_waiting_message."""
    message_model_name = "message_model_one"
    message_model = MessageModel(name=message_model_name)
    process_instance = create_process_instance_from_process_model

    queued_message_send = MessageInstanceModel(
        process_instance_id=process_instance.id,
        bpmn_element_id="something",
        message_type="send",
        message_model=message_model,
    )
