"""ServiceTask_service."""
import sys

# TODO tmp declarations here until airflow provider poetry install is working
operator_module = sys.modules[__name__]

class SlackWebhookOperator:
    def __init__(self, webhook_token="", message="", channel="", **kwargs):
        self.channel = channel
        self.message = message
        self.webhook_token = webhook_token

    def execute(self):
        # TODO log?
        pass

class ServiceTaskService:
    @classmethod
    def available_operators(cls):
        # TODO build dynamically
        # TODO do we define models to add types?
        available_operators = [
            { 
                # TODO probably should be class name, description, etc - the more information
                # the less chance we can get it all just from reflection though
                "name": "SlackWebhookOperator", 
                "parameters": [
                    { "name": "webhook_token", "label": "Webhook Token", "type": "string" },
                    { "name": "message", "label": "Message", "type": "string" },
                    { "name": "channel", "label": "Channel", "type": "string" },
                ]
            },
        ]

        return available_operators

    @classmethod
    def scripting_additions(cls):
        # TODO add types
        operator_names = [operator['name'] for operator in cls.available_operators()]
        scripting_additions = {name: cls._operator_class_from_name(name) for name in operator_names}

    @classmethod
    def _operator_class_from_name(cls, name):
        # TODO add types
        operator_cls = getattr(operator_module, name)
        return operator_cls

