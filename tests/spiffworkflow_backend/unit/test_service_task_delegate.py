"""Test_various_bpmn_constructs."""
from flask.app import Flask
from spiffworkflow_backend.services.secret_service import SecretService
from spiffworkflow_backend.services.service_task_service import ServiceTaskDelegate
from spiffworkflow_backend.services.user_service import UserService
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)


class TestServiceTaskDelegate(BaseTest):

    def test_normalize_value_without_secret(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        result = ServiceTaskDelegate.normalize_value("hey")
        assert result == "hey"

    def test_normalize_value_with_int(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        result = ServiceTaskDelegate.normalize_value(1)
        assert result == 1

    def test_normalize_value_with_secret(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        user = self.find_or_create_user("test_user")
        SecretService().add_secret("hot_secret", "my_secret_value", user.id)
        result = ServiceTaskDelegate.normalize_value("secret:hot_secret")
        assert result == "my_secret_value"
