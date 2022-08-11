"""Test_message_service."""
from flask import Flask
from flask_bpmn.models.db import db
from tests.spiffworkflow_backend.helpers.base_test import BaseTest
from tests.spiffworkflow_backend.helpers.test_data import load_test_spec

from spiffworkflow_backend.models.message_correlation import MessageCorrelationModel
from spiffworkflow_backend.models.message_instance import MessageInstanceModel
from spiffworkflow_backend.models.message_model import MessageModel


class TestSpecFileService(BaseTest):
    """TestSpecFileService."""

    def test_can_check_for_messages_in_bpmn_xml(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
