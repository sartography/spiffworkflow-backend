"""Base_test."""
from flask.app import Flask
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.user_service import UserService


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

    # @staticmethod
    # def get_public_access_token(username: str, password: str) -> dict:
    #     """Get_public_access_token."""
    #     public_access_token = PublicAuthenticationService().get_public_access_token(
    #         username, password
    #     )
    #     return public_access_token
