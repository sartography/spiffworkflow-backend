"""Message_service."""

import flask
from spiffworkflow_backend.models.user import UserModel


class MessageServiceWithAppContext:
    """Wrapper for Message Service.

    This wrappers is to facilitate running the MessageService from the scheduler
    since we need to specify the app context then.
    """

    def __init__(self, app: flask.app.Flask):
        """__init__."""
        self.app = app

    def process_queued_messages_with_app_context(self):
        """Since this runs in a scheduler, we need to specify the app context as well."""
        with self.app.app_context():
            MessageService().process_queued_messages()


class MessageService:
    """MessageService."""

    def process_queued_messages(self):
        """Process_queued_messages."""
        user = UserModel.query.first()
        print(f"user: {user}")
        # MessageInstanceModel.query
        # if
