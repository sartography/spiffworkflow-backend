"""Process Model."""
import pytest
from flask.app import Flask
from flask_bpmn.models.db import db
from tests.spiffworkflow_backend.helpers.base_test import BaseTest

from spiffworkflow_backend.models.permission_target import InvalidPermissionTargetUri, PermissionTargetModel


class TestPermissionTarget(BaseTest):

    def test_asterisk_must_go_at_the_end_of_uri(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        permission_target = PermissionTargetModel(uri="/test_group/*")
        db.session.add(permission_target)
        db.session.commit()

        permission_target = PermissionTargetModel(uri="/test_group")
        db.session.add(permission_target)
        db.session.commit()

        with pytest.raises(InvalidPermissionTargetUri) as exception:
            PermissionTargetModel(uri="/test_group/*/model")
        assert (
            str(exception.value) == "Invalid Permission Target Uri: /test_group/*/model"
        )
