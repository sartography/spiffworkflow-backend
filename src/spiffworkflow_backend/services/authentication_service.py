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
from keycloak import KeycloakOpenID  # type: ignore
from werkzeug.wrappers.response import Response

from spiffworkflow_backend.services.authorization_service import AuthorizationService
# from keycloak.uma_permissions import AuthStatus  # noqa: F401


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

    def logout(self, id_token: str, redirect_url: str | None = None) -> Response:
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

    def get_login_redirect_url(self, state: bytes) -> str:
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
            + f"state={state!r}&"
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

    def get_public_access_token(self, username: str, password: str) -> dict:
        """Get_public_access_token."""
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = AuthorizationService.get_keycloak_args()
        # Get public access token
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        post_data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": "spiffworkflow-frontend",
        }
        public_response = requests.post(request_url, headers=headers, data=post_data)
        if public_response.status_code == 200:
            public_token = json.loads(public_response.text)
            if "access_token" in public_token:
                access_token: dict = public_token["access_token"]
                return access_token
        raise ApiError(
            code="no_public_access_token",
            message=f"We could not get a public access token: {username}",
        )


class AuthenticationService:
    """AuthenticationService."""


class KeycloakAuthenticationService:
    """KeycloakAuthenticationService."""

    @staticmethod
    def get_keycloak_openid(
        server_url: str, client_id: str, realm_name: str, client_secret_key: str
    ) -> KeycloakOpenID:
        """Get_keycloak_openid."""
        keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm_name,
            client_secret_key=client_secret_key,
        )
        return keycloak_openid

    #
    #     @staticmethod
    #     def get_keycloak_token(keycloak_openid, user, password):
    #         """Get_keycloak_token."""
    #         token = keycloak_openid.token(user, password)
    #         return token
    #
    #     @staticmethod
    #     def get_permission_by_token(
    #         keycloak_openid: KeycloakOpenID, token: dict
    #     ) -> Optional[list[dict]]:
    #         """Get_permission_by_token."""
    #         # Get permissions by token
    #         # KEYCLOAK_PUBLIC_KEY = keycloak_openid.public_key()
    #         # KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
    #         # policies = keycloak_openid.get_policies(token['access_token'], method_token_info='decode',
    #         #                                         key=KEYCLOAK_PUBLIC_KEY)
    #         permissions: list = keycloak_openid.get_permissions(  # noqa: S106
    #             token["access_token"], method_token_info="introspect"
    #         )
    #         # TODO: Not sure if this is good. Permissions comes back as None
    #         return permissions
    #
    #     @staticmethod
    #     def get_uma_permissions_by_token(
    #         keycloak_openid: KeycloakOpenID, token: dict
    #     ) -> Optional[list[dict]]:
    #         """Get_uma_permissions_by_token."""
    #         permissions: list = keycloak_openid.uma_permissions(token["access_token"])
    #         return permissions
    #

    @staticmethod
    def get_uma_permissions_by_token_for_resource_and_scope(
        keycloak_openid: KeycloakOpenID, token: dict, resource: str, scope: str
    ) -> Optional[list[dict]]:
        """Get_uma_permissions_by_token_for_resource_and_scope."""
        permissions: list = keycloak_openid.uma_permissions(
            token["access_token"], permissions=f"{resource}#{scope}"
        )
        return permissions


#
#     @staticmethod
#     def get_auth_status_for_resource_and_scope_by_token(
#         keycloak_openid: KeycloakOpenID, token: dict, resource: str, scope: str
#     ) -> AuthStatus:
#         """Get_auth_status_for_resource_and_scope_by_token."""
#         auth_status = keycloak_openid.has_uma_access(
#             token["access_token"], f"{resource}#{scope}"
#         )
#         return auth_status
#
#     @staticmethod
#     def get_keycloak_admin(admin_user=None):
#         """Get_keycloak_admin."""
#         if admin_user is None:
#             admin_user = 'admin'
#         # TODO: Get this to work
#         keycloak_admin = KeycloakAdmin(
#             server_url="http://localhost:7002/",
#             username=admin_user,
#             password=admin_user,
#             realm_name="spiffworkflow",
#             client_id="spiffworkflow-backend",
#             # client_secret_key="seciKpRanUReL0ksZaFm5nfjhMUKHVAO",
#             client_secret_key="JXeQExm0JhQPLumgHtIIqf52bDalHz0q",
#             verify=True,
#         )
#         return keycloak_admin


class KeyCloak:
    """KeyCloak."""

    """Class to interact with KeyCloak server for authorization."""
