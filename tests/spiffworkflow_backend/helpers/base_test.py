"""Base_test."""
from flask.app import Flask

from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.user_service import UserService
from spiffworkflow_backend.services.authentication_service import PublicAuthenticationService


class BaseTest:
    """BaseTest."""

    @staticmethod
    def find_or_create_user(username: str = "test_user1") -> UserModel:
        """Find_or_create_user."""
        user = UserModel.query.filter_by(username=username).first()
        if isinstance(user, UserModel):
            return user

        else:
            user: UserModel = UserService().create_user("local", username, username=username)
            UserService().create_principal(user_id=user.id)

            return user

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

    @staticmethod
    def get_public_access_token(username: str, password: str) -> dict:
        """Get_public_access_token."""
        public_access_token = PublicAuthenticationService().get_public_access_token(
            username, password
        )
        return public_access_token
