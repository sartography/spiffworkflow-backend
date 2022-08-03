"""Message_service."""
from typing import Optional

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
        queued_messages_send = MessageInstanceModel.query.filter_by(
            message_type="send"
        ).all()
        queued_messages_receive = MessageInstanceModel.query.filter_by(
            message_type="receive"
        ).all()
        for queued_message_send in queued_messages_send:
            queued_message_receive = self.get_related_queued_message(
                queued_message_send, queued_messages_receive
            )
            if queued_message_receive:
                self.process_related_message(
                    queued_message_send, queued_message_receive
                )

    def process_related_message(
        self,
        queued_message: MessageInstanceModel,
        related_queued_message: MessageInstanceModel,
    ) -> None:
        """Process_related_message."""
        print(f"queued_message: {queued_message}")
        print(f"related_queued_message: {related_queued_message}")

    def get_related_queued_message(
        self,
        queued_message: MessageInstanceModel,
        related_queued_messages: list[MessageInstanceModel],
    ) -> Optional[MessageInstanceModel]:
        """Get_related_queued_message."""
        message_correlations = MessageCorrelationModel.query.filter_by(
            message_instance_id=queued_message.id
        ).all()
        message_correlation_filter = []
        for message_correlation in message_correlations:
            message_correlation_filter.append(
                and_(
                    MessageCorrelationModel.name == message_correlation.name,
                    MessageCorrelationModel.value == message_correlation.value,
                )
            )

        for queued_message_related in related_queued_messages:

            # sqlalchemy supports select / where statements like active record apparantly
            # https://docs.sqlalchemy.org/en/14/core/tutorial.html#conjunctions
            message_correlation_select = (
                select([db.func.count()])
                .select_from(MessageCorrelationModel)  # type: ignore
                .where(
                    and_(
                        MessageCorrelationModel.message_instance_id
                        == queued_message_related.id,
                        or_(*message_correlation_filter),
                    )
                )
            )
            message_correlations_related = db.session.execute(
                message_correlation_select
            )

            # since the query matches on name, value, and queued_message_related.id, if the counts
            # message correlations found are the same, then this should be the relevant message
            if message_correlations_related.scalar() == len(message_correlations):
                return queued_message_related

        return None
