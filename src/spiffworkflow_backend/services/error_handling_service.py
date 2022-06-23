"""Error_handling_service."""
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService


class ErrorHandlingService:
    """ErrorHandlingService."""

    def handle_error(
        self, _processor: ProcessInstanceProcessor, _error: ApiError
    ) -> None:
        """Handle_error."""
        process_model = ProcessModelService().get_process_model(
            _processor.process_model_identifier, _processor.process_group_identifier
        )
        # If fault_or_suspend_on_exception is not configured, default to `fault`
        if process_model.fault_or_suspend_on_exception == "suspend":
            ...
        else:
            # fault
            ...
        if len(process_model.exception_notification_addresses) > 0:
            try:
                # some email notification method
                ...
            except Exception as e:
                # hmm...
                print(e)
        print("handle_error")


class FailingService:
    """FailingService."""

    @staticmethod
    def fail_as_service() -> None:
        """It fails."""
        raise ApiError(code="bad_service", message="This is my failing service")
