"""Test_message_service."""
from spiffworkflow_backend.services.message_service import MessageService
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from flask import Flask
from flask_bpmn.models.db import db

from spiffworkflow_backend.models.message_correlation import MessageCorrelationModel
from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.message_model import MessageModel


class TestMessageService(BaseTest):
    """TestMessageService."""

    def test_can_send_message_to_waiting_message(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_can_send_message_to_waiting_message."""
        message_model_identifier = "message_model_one"
        message_model = MessageModel(identifier=message_model_identifier)
        db.session.add(message_model)
        db.session.commit()

        process_model = load_test_spec("hello_world")
        process_instance_send = self.create_process_instance_from_process_model(
            process_model, "waiting"
        )
        process_instance_receive = self.create_process_instance_from_process_model(
            process_model, "waiting"
        )

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

        message_correlation_one_send = MessageCorrelationModel(
            message_instance_id=queued_message_send.id,
            name="name1",
            value="value1",
        )

        message_correlation_one_receive = MessageCorrelationModel(
            message_instance_id=queued_message_receive.id,
            name="name1",
            value="value1",
        )

        message_correlation_two_send = MessageCorrelationModel(
            message_instance_id=queued_message_send.id,
            name="name2",
            value="value2",
        )

        message_correlation_two_receive = MessageCorrelationModel(
            message_instance_id=queued_message_receive.id,
            name="name2",
            value="value2",
        )
        db.session.add(message_correlation_one_send)
        db.session.add(message_correlation_one_receive)
        db.session.add(message_correlation_two_send)
        db.session.add(message_correlation_two_receive)
        db.session.commit()

        MessageService().process_queued_messages()
        print(queued_message_send.failure_cause)
        print(queued_message_send.status)
