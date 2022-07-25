"""Base_test."""
from flask.app import Flask


class BaseTest:
    """BaseTest."""

    @staticmethod
    def get_keycloak_constants(app: Flask) -> tuple:
        """Get_keycloak_constants."""
        keycloak_server_url = app.config['KEYCLOAK_SERVER_URL']
        keycloak_client_id = app.config["KEYCLOAK_CLIENT_ID"]
        keycloak_realm_name = app.config["KEYCLOAK_REALM_NAME"]
        keycloak_client_secret_key = app.config["KEYCLOAK_CLIENT_SECRET_KEY"]  # noqa: S105

        return keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
