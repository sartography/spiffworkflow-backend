"""Test_secret_service."""

from flask.app import Flask
from flask.testing import FlaskClient
from tests.spiffworkflow_backend.helpers.base_test import BaseTest

from spiffworkflow_backend.models.secret_model import SecretModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.secret_service import SecretService


class TestSecretService(BaseTest):
    """TestSecretService."""

    test_key = "test_key"
    test_value = "test_value"

    def add_test_secret(self, user: UserModel) -> SecretModel:
        """Add_test_secret."""
        return SecretService().add_secret(self.test_key, self.test_value, user.id)

    def test_add_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test_add_secret."""
        user = self.find_or_create_user()
        test_secret = self.add_test_secret(user)

        assert test_secret is not None
        assert test_secret.key == self.test_key
        assert test_secret.value == self.test_value
        assert test_secret.creator_user_id == user.id

    def test_get_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
        """Test_get_secret."""
        user = self.find_or_create_user()
        self.add_test_secret(user)

        secret = SecretService().get_secret(self.test_key)
        assert secret is not None
        assert secret == self.test_value

    def test_get_secret_bad_key(
        self, app: Flask, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test_get_secret_bad_service."""
        user = self.find_or_create_user()
        self.add_test_secret(user)

        bad_secret = SecretService().get_secret("bad_key")
        assert bad_secret is None

    # def test_secret_add_allowed_process(
    #     self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    # ) -> None:
    #     """Test_secret_add_allowed_process."""
    #     process_group_id = "test"
    #     process_group_display_name = "My Test Process Group"
    #
    #     user = self.find_or_create_user()
    #     self.create_process_group(
    #         client, user, process_group_id, display_name=process_group_display_name
    #     )
    #
    #     process_model_id = "make_cookies"
    #     process_model_display_name = "Cooooookies"
    #     process_model_description = "Om nom nom delicious cookies"
    #     self.create_process_model(
    #         client,
    #         process_group_id=process_group_id,
    #         process_model_id=process_model_id,
    #         process_model_display_name=process_model_display_name,
    #         process_model_description=process_model_description,
    #     )
    #
    #     process_model_info = ProcessModelService().get_process_model(
    #         process_model_id, process_group_id
    #     )
    #     process_model_relative_path = FileSystemService.process_model_relative_path(
    #         process_model_info
    #     )
    #
    #     test_secret = self.add_test_secret(user)
    #     allowed_process_model = SecretService().add_allowed_process(
    #         secret_id=test_secret.id, allowed_relative_path=process_model_relative_path
    #     )
    #     assert allowed_process_model is not None
    #     assert isinstance(allowed_process_model, SecretAllowedProcessPathModel)
    #     assert allowed_process_model.secret_id == test_secret.id
    #     assert (
    #         allowed_process_model.allowed_relative_path == process_model_relative_path
    #     )
    #
    #     assert len(test_secret.allowed_processes) == 1
    #     assert test_secret.allowed_processes[0] == allowed_process_model

    def test_update_secret(self) -> None:
        """Test update secret."""
        ...

    def test_delete_secret(
        self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
    ) -> None:
        """Test delete secret."""
        user = self.find_or_create_user()
        self.add_test_secret(user)
        SecretService.delete_secret(self.test_key)


# class TestSecretServiceApi(BaseTest):
#     """TestSecretServiceApi."""
#
#     test_service = "test_service"
#     test_client = "test_client"
#     test_key = "1234567890"
#
#     def test_add_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test_add_secret."""
#         user = self.find_or_create_user()
#         secret_model = SecretModel(
#             service=self.test_service,
#             client=self.test_client,
#             key=self.test_key,
#             creator_user_id=user.id,
#         )
#         # data = json.dumps({"service": self.test_service,
#         #                    "client": self.test_client,
#         #                    "key": self.test_key})
#         data = json.dumps(SecretModelSchema().dump(secret_model))
#         response = client.post(
#             "/v1.0/secrets",
#             headers=self.logged_in_headers(user),
#             content_type="application/json",
#             data=data,
#         )
#         print(response)
#
#     def test_get_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test get secret."""
#         ...
#
#     def test_delete_secret(
#         self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None
#     ) -> None:
#         """Test delete secret."""
#         ...
