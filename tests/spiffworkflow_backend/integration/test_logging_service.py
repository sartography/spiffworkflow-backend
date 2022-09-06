"""Test_logging_service."""
from flask.app import Flask
from flask.testing import FlaskClient
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import logged_in_headers


class TestLoggingService(BaseTest):
    """Test logging service."""

    def test_logging_service_spiff_logger(
        self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_process_instance_run."""
        process_group_id = "test_logging_spiff_logger"
        process_model_id = "simple_script"
        user = self.find_or_create_user()
        headers = logged_in_headers(user)
        response = self.create_process_instance(
            client, process_group_id, process_model_id, headers
        )
        assert response.json is not None
        process_instance_id = response.json["id"]
        response = client.post(
            f"/v1.0/process-models/{process_group_id}/{process_model_id}/process-instances/{process_instance_id}/run",
            headers=logged_in_headers(user),
        )
        assert response.status_code == 200

        assert response.json is not None
