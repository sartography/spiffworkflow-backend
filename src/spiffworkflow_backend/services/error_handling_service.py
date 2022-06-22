"""Error_handling_service."""
from flask_bpmn.api.api_error import ApiError
from spiffworkflow_backend.services.process_instance_processor import ProcessInstanceProcessor


class ErrorHandlingService:
    """ErrorHandlingService."""

    def handle_error(self, _processor: ProcessInstanceProcessor, _error: ApiError) -> None:
        """Handle_error."""
        print("handle_error")


class FailingService:
    """FailingService."""

    @staticmethod
    def fail_as_service() -> None:
        """It fails."""
        raise ApiError(code="bad_service", message="This is my failing service")
