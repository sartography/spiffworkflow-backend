"""ServiceTask_service."""

class ServiceTaskService:
    @classmethod
    def available_operators(cls):
        available_operators = [
            { 
                "name": "SlackWebhookOperator", 
                "parameters": [
                    { "name": "webhook_token", "label": "Webhook Token", "type": "string" },
                    { "name": "message", "label": "Message", "type": "string" },
                    { "name": "channel", "label": "Channel", "type": "string" },
                ]
            },
        ]

        return available_operators
