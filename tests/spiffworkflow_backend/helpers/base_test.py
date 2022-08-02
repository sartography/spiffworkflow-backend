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

        user = UserService().create_user("local", username, username=username)
        if isinstance(user, UserModel):
            UserService().create_principal(user_id=user.id)
            return user

        raise ApiError(
            code="create_user_error", message=f"Cannot find or create user: {username}"
        )

    @staticmethod
    def get_keycloak_constants(app: Flask) -> tuple:
        """Get_keycloak_constants."""
        keycloak_server_url = app.config["KEYCLOAK_SERVER_URL"]
        keycloak_client_id = app.config["KEYCLOAK_CLIENT_ID"]
        keycloak_realm_name = app.config["KEYCLOAK_REALM_NAME"]
        keycloak_client_secret_key = app.config[
            "KEYCLOAK_CLIENT_SECRET_KEY"
        ]  # noqa: S105

        return (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        )

    # @staticmethod
    # def get_public_access_token(username: str, password: str) -> dict:
    #     """Get_public_access_token."""
    #     public_access_token = PublicAuthenticationService().get_public_access_token(
    #         username, password
    #     )
    #     return public_access_token
