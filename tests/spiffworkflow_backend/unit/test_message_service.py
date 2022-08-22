"""Test_message_service."""
from flask import Flask
from spiffworkflow_backend.routes.process_api_blueprint import process_instance_show
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.models.message_correlation import MessageCorrelationModel
from spiffworkflow_backend.models.message_correlation_message_instance import (
    MessageCorrelationMessageInstanceModel,
)
from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.services.message_service import MessageService
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)
from spiffworkflow_backend.services.user_service import UserService


class TestMessageService(BaseTest):
    """TestMessageService."""

    def test_can_send_message_to_waiting_message(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_can_send_message_to_waiting_message."""
        process_model_sender = load_test_spec("message_sender")
        load_test_spec("message_receiver")
        system_user = UserService().find_or_create_user(
            service="internal", service_id="system_user"
        )

        process_instance_sender = ProcessInstanceService.create_process_instance(
            process_model_sender.id,
            system_user,
            process_group_identifier=process_model_sender.process_group_id,
        )
        processor_sender = ProcessInstanceProcessor(process_instance_sender)
        processor_sender.do_engine_steps()
        processor_sender.save()

        message_instance_result = MessageInstanceModel.query.all()
        assert len(message_instance_result) == 2
        # ensure both message instances are for the same process instance
        # it will be send_message and receive_message_response
        assert (
            message_instance_result[0].process_instance_id
            == message_instance_result[1].process_instance_id
        )

        message_instance_sender = message_instance_result[0]
        assert message_instance_sender.process_instance_id == process_instance_sender.id
        message_correlations = MessageCorrelationModel.query.all()
        assert len(message_correlations) == 2
        assert message_correlations[0].process_instance_id == process_instance_sender.id
        message_correlations_message_instances = (
            MessageCorrelationMessageInstanceModel.query.all()
        )
        assert len(message_correlations_message_instances) == 4
        assert (
            message_correlations_message_instances[0].message_instance_id
            == message_instance_sender.id
        )
        assert (
            message_correlations_message_instances[1].message_instance_id
            == message_instance_sender.id
        )
        assert (
            message_correlations_message_instances[2].message_instance_id
            == message_instance_result[1].id
        )
        assert (
            message_correlations_message_instances[3].message_instance_id
            == message_instance_result[1].id
        )

        # process first message
        MessageService().process_message_instances()
        assert message_instance_sender.status == "completed"

        process_instance_result = ProcessInstanceModel.query.all()

        assert len(process_instance_result) == 2
        process_instance_receiver = process_instance_result[1]

        # just make sure it's a different process instance
        assert process_instance_receiver.id != process_instance_sender.id
        assert process_instance_receiver.status == "complete"

        message_instance_result = MessageInstanceModel.query.all()
        assert len(message_instance_result) == 3
        message_instance_receiver = message_instance_result[1]
        assert message_instance_receiver.id != message_instance_sender.id
        assert message_instance_receiver.status == "ready"

        # process second message
        MessageService().process_message_instances()

        message_instance_result = MessageInstanceModel.query.all()
        assert len(message_instance_result) == 3
        for message_instance in message_instance_result:
            assert message_instance.status == 'completed'

        process_instance_result = ProcessInstanceModel.query.all()
        assert len(process_instance_result) == 2
        for process_instance in process_instance_result:
            assert process_instance.status == 'complete'
