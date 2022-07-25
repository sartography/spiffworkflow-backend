"""Authentication_service."""
from typing import Optional

import requests
import base64
import json
import enum
from flask import g
from flask import current_app

from keycloak import KeycloakOpenID  # type: ignore
from keycloak.uma_permissions import AuthStatus  # type: ignore
from keycloak import KeycloakAdmin

from spiffworkflow_backend.services.authorization_service import AuthorizationService


class AuthenticationServiceProviders(enum.Enum):
    keycloak = 'keycloak'
    internal = 'internal'


class PublicAuthenticationService:
    """Not sure where/if this ultimately lives.
    It uses a separate public keycloak client: spiffworkflow-frontend
    Used during development to make testing easy.
    """
    def get_public_access_token(self, username, password) -> dict:
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()
        # Get public access token
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        post_data = {'grant_type': 'password',
                     'username': username,
                     'password': password,
                     'client_id': 'spiffworkflow-frontend'
                     }
        public_response = requests.post(request_url, headers=headers, data=post_data)
        public_token = json.loads(public_response.text)

        return public_token['access_token']


class AuthenticationService:
    """AuthenticationService."""




class KeycloakAuthenticationService:

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

    """Class to interact with KeyCloak server for authorization"""