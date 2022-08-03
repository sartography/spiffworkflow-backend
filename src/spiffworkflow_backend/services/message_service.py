"""Message_service."""
import flask
from flask_bpmn.models.db import db
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import select

from spiffworkflow_backend.models.message_correlation import MessageCorrelationModel
from spiffworkflow_backend.models.message_instance import MessageInstanceModel


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


class MessageService:
    """MessageService."""

    def process_queued_messages(self) -> None:
        """Process_queued_messages."""
        queued_messages_send = MessageInstanceModel.query.filter_by(message_type="send")
        queued_messages_receive = MessageInstanceModel.query.filter_by(
            message_type="receive"
        )
        for queued_message_send in queued_messages_send:
            print(f"queued_message_send.id: {queued_message_send.id}")
            message_correlations_send = MessageCorrelationModel.query.filter_by(
                message_instance_id=queued_message_send.id
            )
            message_correlation_filter = []
            for m in message_correlations_send:
                message_correlation_filter.append(
                    and_(
                        MessageCorrelationModel.name == m.name,
                        MessageCorrelationModel.value == m.value,
                    )
                )

            for queued_message_receive in queued_messages_receive:

                # sqlalchemy supports select / where statements like active record apparantly
                # https://docs.sqlalchemy.org/en/14/core/tutorial.html#conjunctions
                message_correlation_select = select(MessageCorrelationModel).where(  # type: ignore
                    and_(
                        MessageCorrelationModel.message_instance_id
                        == queued_message_receive.id,
                        or_(*message_correlation_filter),
                    )
                )
                print(f"queued_message_receive.id: {queued_message_receive.id}")
                message_correlations = db.session.execute(message_correlation_select)
                for mc in message_correlations:
                    print(
                        f"message_correlations: {mc.MessageCorrelationModel.message_instance_id}"
                    )
