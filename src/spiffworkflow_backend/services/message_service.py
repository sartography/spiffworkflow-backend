"""Message_service."""
from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition  # type: ignore
from typing import Optional

import flask
from flask_bpmn.models.db import db
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import select

from spiffworkflow_backend.models.message_correlation import MessageCorrelationModel
from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)


class MessageServiceWithAppContext:
    """Wrapper for Message Service.

    This wrappers is to facilitate running the MessageService from the scheduler
    since we need to specify the app context then.
    """

    def __init__(self, app: flask.app.Flask):
        """__init__."""
        self.app = app

    def process_queued_messages_with_app_context(self) -> None:
        """Since this runs in a scheduler, we need to specify the app context as well."""
        with self.app.app_context():
            MessageService().process_queued_messages()


class MessageServiceError(Exception):
    """MessageServiceError."""


class MessageService:
    """MessageService."""

    def process_queued_messages(self) -> None:
        """Process_queued_messages."""
        queued_messages_send = MessageInstanceModel.query.filter_by(
            message_type="send", status="ready"
        ).all()
        queued_messages_receive = MessageInstanceModel.query.filter_by(
            message_type="receive"
        ).all()
        for queued_message_send in queued_messages_send:
            # check again in case another background process picked up the message
            # while the previous one was running
            if queued_message_send.status != "receive":
                continue

            queued_message_send.status = "running"
            db.session.add(queued_message_send)
            db.session.commit()

            queued_message_receive = None
            try:
                queued_message_receive = self.get_queued_message_receive(
                    queued_message_send, queued_messages_receive
                )
                if queued_message_receive:
                    self.process_message_receive(
                        queued_message_send, queued_message_receive
                    )
                    queued_message_receive.status = "completed"
                    db.session.add(queued_message_receive)

                queued_message_send.status = "completed"
                db.session.add(queued_message_send)
                db.session.commit()
            except Exception as exception:
                queued_message_send.status = "failed"
                queued_message_send.failure_cause = str(exception)
                db.session.add(queued_message_send)

                if queued_message_receive:
                    queued_message_receive.status = "failed"
                    queued_message_receive.failure_cause = str(exception)
                    db.session.add(queued_message_receive)

                db.session.commit()

    def process_message_receive(
        self,
        queued_message_send: MessageInstanceModel,
        queued_message_receive: MessageInstanceModel,
    ) -> None:
        """Process_message_receive."""
        process_instance_send = ProcessInstanceModel.query.filter_by(
            id=queued_message_send.process_instance_id
        ).first()
        if process_instance_send is None:
            raise MessageServiceError(
                f"Process instance cannot be found for message: {queued_message_send.id}."
                f"Tried with id {queued_message_send.process_instance_id}"
            )

        processor_send = ProcessInstanceProcessor(process_instance_send)
        spiff_task_send = processor_send.bpmn_process_instance.get_task_by_id(
            queued_message_send.bpmn_element_id
        )
        if spiff_task_send is None:
            raise MessageServiceError(
                "Processor failed to obtain task.",
            )

        message_event_send = MessageEventDefinition(
            spiff_task_send.id, payload=spiff_task_send.payload
        )

        process_instance_receive = ProcessInstanceModel.query.filter_by(
            id=queued_message_receive.process_instance_id
        ).first()
        if process_instance_receive is None:
            raise MessageServiceError(
                (
                    f"Process instance cannot be found for queued message: {queued_message_receive.id}."
                    f"Tried with id {queued_message_receive.process_instance_id}",
                )
            )

        processor_receive = ProcessInstanceProcessor(process_instance_receive)
        processor_receive.bpmn_process_instance.catch(message_event_send)

    def get_queued_message_receive(
        self,
        queued_message_send: MessageInstanceModel,
        queued_messages_receive: list[MessageInstanceModel],
    ) -> Optional[MessageInstanceModel]:
        """Get_queued_message_receive."""
        message_correlations_send = MessageCorrelationModel.query.filter_by(
            message_instance_id=queued_message_send.id
        ).all()
        message_correlation_filter = []
        for message_correlation_send in message_correlations_send:
            message_correlation_filter.append(
                and_(
                    MessageCorrelationModel.name == message_correlation_send.name,
                    MessageCorrelationModel.value == message_correlation_send.value,
                )
            )

        for queued_message_receive in queued_messages_receive:

            # sqlalchemy supports select / where statements like active record apparantly
            # https://docs.sqlalchemy.org/en/14/core/tutorial.html#conjunctions
            message_correlation_select = (
                select([db.func.count()])
                .select_from(MessageCorrelationModel)  # type: ignore
                .where(
                    and_(
                        MessageCorrelationModel.message_instance_id
                        == queued_message_receive.id,
                        or_(*message_correlation_filter),
                    )
                )
            )
            message_correlations_receive = db.session.execute(
                message_correlation_select
            )

            # since the query matches on name, value, and queued_message_receive.id, if the counts
            # message correlations found are the same, then this should be the relevant message
            if message_correlations_receive.scalar() == len(message_correlations_send):
                return queued_message_receive

        return None
