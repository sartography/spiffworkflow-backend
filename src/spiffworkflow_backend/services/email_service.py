"""Email_service."""
from flask import current_app
from flask_mail import Message  # type: ignore
from typing import List, Optional

class EmailService:
    """Provides common interface for working with an Email."""

    @staticmethod
    def add_email(
        subject: str,
        sender: str,
        recipients: List[str],
        content: str,
        content_html: str,
        cc: Optional[str]=None,
        bcc: Optional[str]=None,
        reply_to: Optional[str]=None,
        attachment_files: Optional[dict]=None,
    ) ->None:
        """We will receive all data related to an email and send it."""
        mail = current_app.config["MAIL_APP"]

        # Send mail
        try:
            msg = Message(
                subject,
                sender=sender,
                recipients=recipients,
                body=content,
                html=content_html,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
            )

            if attachment_files is not None:
                for file in attachment_files:
                    msg.attach(file["name"], file["type"], file["data"])

            mail.send(msg)

        except Exception as e:
            # app.logger.error('An exception happened in EmailService', exc_info=True)
            # app.logger.error(str(e))
            raise e
