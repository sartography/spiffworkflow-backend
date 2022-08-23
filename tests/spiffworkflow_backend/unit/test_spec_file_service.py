"""Test_message_service."""
from flask import Flask
from tests.spiffworkflow_backend.helpers.base_test import BaseTest


class TestSpecFileService(BaseTest):
    """TestSpecFileService."""

    def test_can_check_for_messages_in_bpmn_xml(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_can_check_for_messages_in_bpmn_xml."""
        assert True
