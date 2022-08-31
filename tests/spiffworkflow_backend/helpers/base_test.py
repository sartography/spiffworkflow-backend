"""Base_test."""
import io
import json
import time

from flask.app import Flask
from flask.testing import FlaskClient
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db

from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_model import NotificationType
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.user_service import UserService

from tests.spiffworkflow_backend.helpers.test_data import load_test_spec
from tests.spiffworkflow_backend.helpers.test_data import logged_in_headers

from typing import Any
from typing import Dict
from typing import Optional

from werkzeug.test import TestResponse


class BaseTest:
    """BaseTest."""

    @staticmethod
    def find_or_create_user(username: str = "test_user1") -> UserModel:
        """Find_or_create_user."""
        user = UserModel.query.filter_by(username=username).first()
        if isinstance(user, UserModel):
            return user

        user = UserService().create_user("internal", username, username=username)
        if isinstance(user, UserModel):
            UserService().create_principal(user_id=user.id)
            return user

        raise ApiError(
            code="create_user_error", message=f"Cannot find or create user: {username}"
        )

    @staticmethod
    def get_open_id_constants(app: Flask) -> tuple:
        """Get_open_id_constants."""
        open_id_server_url = app.config["OPEN_ID_SERVER_URL"]
        open_id_client_id = app.config["OPEN_ID_CLIENT_ID"]
        open_id_realm_name = app.config["OPEN_ID_REALM_NAME"]
        open_id_client_secret_key = app.config[
            "OPEN_ID_CLIENT_SECRET_KEY"
        ]  # noqa: S105

        return (
            open_id_server_url,
            open_id_client_id,
            open_id_realm_name,
            open_id_client_secret_key,
        )

    def create_process_instance(
        self,
        client: FlaskClient,
        test_process_group_id: str,
        test_process_model_id: str,
        headers: Dict[str, str],
    ) -> TestResponse:
        """Create_process_instance."""
        load_test_spec(test_process_model_id, process_group_id=test_process_group_id)
        response = client.post(
            f"/v1.0/process-models/{test_process_group_id}/{test_process_model_id}/process-instances",
            headers=headers,
        )
        assert response.status_code == 201
        return response

    def create_process_model(
        self,
        client: FlaskClient,
        process_group_id: Optional[str] = None,
        process_model_id: Optional[str] = None,
        process_model_display_name: Optional[str] = None,
        process_model_description: Optional[str] = None,
        fault_or_suspend_on_exception: Optional[str] = None,
        exception_notification_addresses: Optional[list] = None,
        primary_process_id: Optional[str] = None,
        primary_file_name: Optional[str] = None,
    ) -> TestResponse:
        """Create_process_model."""
        process_model_service = ProcessModelService()

        # make sure we have a group
        if process_group_id is None:
            process_group_tmp = ProcessGroup(
                id="test_cat",
                display_name="Test Category",
                display_order=0,
                admin=False,
            )
            process_group = process_model_service.add_process_group(process_group_tmp)
        else:
            process_group = ProcessModelService().get_process_group(process_group_id)

        if process_model_id is None:
            process_model_id = "make_cookies"
        if process_model_display_name is None:
            process_model_display_name = "Cooooookies"
        if process_model_description is None:
            process_model_description = "Om nom nom delicious cookies"
        if fault_or_suspend_on_exception is None:
            fault_or_suspend_on_exception = NotificationType.suspend.value
        if exception_notification_addresses is None:
            exception_notification_addresses = []
        if primary_process_id is None:
            primary_process_id = ""
        if primary_file_name is None:
            primary_file_name = ""
        model = ProcessModelInfo(
            id=process_model_id,
            display_name=process_model_display_name,
            description=process_model_description,
            process_group_id=process_group.id,
            standalone=False,
            is_review=False,
            is_master_spec=False,
            libraries=[],
            library=False,
            primary_process_id=primary_process_id,
            primary_file_name=primary_file_name,
            fault_or_suspend_on_exception=fault_or_suspend_on_exception,
            exception_notification_addresses=exception_notification_addresses,
        )
        user = self.find_or_create_user()
        response = client.post(
            "/v1.0/process-models",
            content_type="application/json",
            data=json.dumps(ProcessModelInfoSchema().dump(model)),
            headers=logged_in_headers(user),
        )
        assert response.status_code == 201
        return response

    def create_spec_file(
        self,
        client: FlaskClient,
        process_group_id: str = "",
        process_model_id: str = "",
        file_name: str = "",
        file_data: bytes = b"",
    ) -> Any:
        """Test_create_spec_file."""
        if process_group_id == "":
            process_group_id = "random_fact"
        if process_model_id == "":
            process_model_id = "random_fact"
        if file_name == "":
            file_name = "random_fact.svg"
        if file_data == b"":
            file_data = b"abcdef"
        spec = load_test_spec(process_model_id, process_group_id=process_group_id)
        data = {"file": (io.BytesIO(file_data), file_name)}
        user = self.find_or_create_user()
        response = client.post(
            f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file",
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers=logged_in_headers(user),
        )
        assert response.status_code == 201
        assert response.get_data() is not None
        file = json.loads(response.get_data(as_text=True))
        # assert FileType.svg.value == file["type"]
        # assert "image/svg+xml" == file["content_type"]

        response = client.get(
            f"/v1.0/process-models/{spec.process_group_id}/{spec.id}/file/{file_name}",
            headers=logged_in_headers(user),
        )
        assert response.status_code == 200
        file2 = json.loads(response.get_data(as_text=True))
        assert file["file_contents"] == file2["file_contents"]
        return file

    def create_process_group(
        self,
        client: FlaskClient,
        user: Any,
        process_group_id: str,
        display_name: str = "",
    ) -> str:
        """Create_process_group."""
        process_group = ProcessGroup(
            id=process_group_id, display_name=display_name, display_order=0, admin=False
        )
        response = client.post(
            "/v1.0/process-groups",
            headers=logged_in_headers(user),
            content_type="application/json",
            data=json.dumps(ProcessGroupSchema().dump(process_group)),
        )
        assert response.status_code == 201
        assert response.json is not None
        assert response.json["id"] == process_group_id
        return process_group_id


    # @staticmethod
    # def get_public_access_token(username: str, password: str) -> dict:
    #     """Get_public_access_token."""
    #     public_access_token = PublicAuthenticationService().get_public_access_token(
    #         username, password
    #     )
    #     return public_access_token

    def create_process_instance_from_process_model(
        self, process_model: ProcessModelInfo, status: str
    ) -> ProcessInstanceModel:
        """Create_process_instance_from_process_model."""
        user = self.find_or_create_user()
        current_time = round(time.time())
        process_instance = ProcessInstanceModel(
            status=status,
            process_initiator=user,
            process_model_identifier=process_model.id,
            process_group_identifier=process_model.process_group_id,
            updated_at_in_seconds=round(time.time()),
            start_in_seconds=current_time - (3600 * 1),
            end_in_seconds=current_time - (3600 * 1 - 20),
        )
        db.session.add(process_instance)
        db.session.commit()
        return process_instance
