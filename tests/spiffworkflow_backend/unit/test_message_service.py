"""Test_message_service."""
from flask import Flask
from flask_bpmn.models.db import db
from tests.spiffworkflow_backend.helpers.base_test import BaseTest

from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.message_model import MessageModel
from spiffworkflow_backend.services.message_service import MessageService
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec


class TestAuthentication(BaseTest):
    """TestAuthentication."""

    def test_can_send_message_to_waiting_message(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test_can_send_message_to_waiting_message."""
        message_model_name = "message_model_one"
        message_model = MessageModel(name=message_model_name)
        db.session.add(message_model)
        db.session.commit()

        process_model = load_test_spec('hello_world')
        process_instance_send = self.create_process_instance_from_process_model(process_model, 'waiting')
        process_instance_receive = self.create_process_instance_from_process_model(process_model, 'waiting')

        queued_message_send = MessageInstanceModel(
            process_instance_id=process_instance_send.id,
            bpmn_element_id="something",
            message_type="send",
            message_model_id=message_model.id,
        )

        queued_message_receive = MessageInstanceModel(
            process_instance_id=process_instance_receive.id,
            bpmn_element_id="something",
            message_type="receive",
            message_model_id=message_model.id,
        )

        db.session.add(queued_message_send)
        db.session.add(queued_message_receive)
        db.session.commit()

        MessageService().process_queued_messages()
