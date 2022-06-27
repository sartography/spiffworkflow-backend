from flask import current_app
from flask_mail import Message


class EmailService(object):
    """Provides common interface for working with an Email"""

    @staticmethod
    def add_email(subject, sender, recipients, content, content_html,
                  cc=None, bcc=None, study_id=None, reply_to=None, attachment_files=None, workflow_spec_id=None, name=None):
        """We will receive all data related to an email and send it"""
        mail = current_app.config["MAIL_APP"]

        # Send mail
        try:
            msg = Message(subject,
                          sender=sender,
                          recipients=recipients,
                          body=content,
                          html=content_html,
                          cc=cc,
                          bcc=bcc,
                          reply_to=reply_to)

            if attachment_files is not None:
                for file in attachment_files:
                    msg.attach(file['name'], file['type'], file['data'])

            mail.send(msg)

        except Exception as e:
            # app.logger.error('An exception happened in EmailService', exc_info=True)
            # app.logger.error(str(e))
            raise e
