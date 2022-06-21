"""Error_handling_service."""
from flask_bpmn.api.api_error import ApiError


class ErrorHandlingService:
    """ErrorHandlingService."""

    def handle_error(self, processor, error):
        """Handle_error."""
        print("handle_error")


class FailingService:
    """FailingService."""

    @staticmethod
    def fail_as_service():
        """It fails."""
        raise ApiError(code="bad_service", message="This is my failing service")
