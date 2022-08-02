"""Authentication_service."""
import base64
import enum
import json
import time
from typing import Optional

import jwt
import requests
from flask import current_app
from flask import redirect
from flask_bpmn.api.api_error import ApiError
from werkzeug.wrappers.response import Response


def get_keycloak_args() -> tuple:
    """Get_keycloak_args."""
    keycloak_server_url = current_app.config["KEYCLOAK_SERVER_URL"]
    keycloak_client_id = current_app.config["KEYCLOAK_CLIENT_ID"]
    keycloak_realm_name = current_app.config["KEYCLOAK_REALM_NAME"]
    keycloak_client_secret_key = current_app.config[
        "KEYCLOAK_CLIENT_SECRET_KEY"
    ]  # noqa: S105
    return (
        keycloak_server_url,
        keycloak_client_id,
        keycloak_realm_name,
        keycloak_client_secret_key,
    )


class AuthenticationServiceProviders(enum.Enum):
    """AuthenticationServiceProviders."""

    keycloak = "keycloak"
    internal = "internal"


class PublicAuthenticationService:
    """PublicAuthenticationService."""

    """Not sure where/if this ultimately lives.
    It uses a separate public keycloak client: spiffworkflow-frontend
    Used during development to make testing easy.
    """

    def logout(self, id_token: str, redirect_url: Optional[str] = None) -> Response:
        """Logout."""
        if redirect_url is None:
            redirect_url = "/"
        return_redirect_url = "http://localhost:7000/v1.0/logout_return"
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = get_keycloak_args()
        request_url = (
            f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/logout?"
            + f"post_logout_redirect_uri={return_redirect_url}&"
            + f"id_token_hint={id_token}"
        )

        return redirect(request_url)

    @staticmethod
    def generate_state(redirect_url: str) -> bytes:
        """Generate_state."""
        state = base64.b64encode(bytes(str({"redirect_url": redirect_url}), "UTF-8"))
        return state

    def get_login_redirect_url(self, state: str) -> str:
        """Get_login_redirect_url."""
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = get_keycloak_args()
        return_redirect_url = "http://localhost:7000/v1.0/login_return"
        login_redirect_url = (
            f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/auth?"
            + f"state={state}&"
            + "response_type=code&"
            + f"client_id={keycloak_client_id}&"
            + "scope=openid&"
            + f"redirect_uri={return_redirect_url}"
        )
        return login_redirect_url

    def get_id_token_object(self, code: str) -> dict:
        """Get_id_token_object."""
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = get_keycloak_args()

        backend_basic_auth_string = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        backend_basic_auth_bytes = bytes(backend_basic_auth_string, encoding="ascii")
        backend_basic_auth = base64.b64encode(backend_basic_auth_bytes)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {backend_basic_auth.decode('utf-8')}",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:7000/v1.0/login_return",
        }

        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"

        response = requests.post(request_url, data=data, headers=headers)
        id_token_object: dict = json.loads(response.text)
        return id_token_object

    @staticmethod
    def validate_id_token(id_token: str) -> bool:
        """Https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation."""
        valid = True
        now = time.time()
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = get_keycloak_args()
        try:
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        except Exception as e:
            raise ApiError(
                code="bad_id_token", message="Cannot decode id_token", status_code=401
            ) from e
        if (
            decoded_token["iss"]
            != f"{keycloak_server_url}/realms/{keycloak_realm_name}"
        ):
            valid = False
        elif (
            keycloak_client_id not in decoded_token["aud"]
            and "account" not in decoded_token["aud"]
        ):
            valid = False
        elif "azp" in decoded_token and decoded_token["azp"] not in (
            keycloak_client_id,
            "account",
        ):
            valid = False
        elif now < decoded_token["iat"]:
            valid = False

        if not valid:
            current_app.logger.error(f"Invalid token in validate_id_token: {id_token}")
            return False

        if now > decoded_token["exp"]:
            raise ApiError(
                code="invalid_token",
                message="Your token is expired. Please Login",
                status_code=401,
            )

        return True
