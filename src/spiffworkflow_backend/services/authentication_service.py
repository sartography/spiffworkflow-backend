"""Authentication_service."""
from typing import Optional

import requests
import base64
import json
import enum
import random
import jwt
import time
from flask import g
from flask import current_app
from flask import redirect
from flask_bpmn.api.api_error import ApiError

from keycloak import KeycloakOpenID  # type: ignore
from keycloak.uma_permissions import AuthStatus  # type: ignore
from keycloak import KeycloakAdmin

from spiffworkflow_backend.services.authorization_service import AuthorizationService


def get_keycloak_args():
    keycloak_server_url = current_app.config['KEYCLOAK_SERVER_URL']
    keycloak_client_id = current_app.config["KEYCLOAK_CLIENT_ID"]
    keycloak_realm_name = current_app.config["KEYCLOAK_REALM_NAME"]
    keycloak_client_secret_key = current_app.config["KEYCLOAK_CLIENT_SECRET_KEY"]  # noqa: S105
    return keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key


class AuthenticationServiceProviders(enum.Enum):
    keycloak = 'keycloak'
    internal = 'internal'


class PublicAuthenticationService:
    """Not sure where/if this ultimately lives.
    It uses a separate public keycloak client: spiffworkflow-frontend
    Used during development to make testing easy.
    """
    def logout(self, redirect_url: str='/', id_token: str | None=None):
        if id_token is None:
            raise ApiError(code='missing_id_token',
                           message="id_token is missing",
                           status_code=400)

        return_redirect_url = 'http://localhost:7000/v1.0/logout_return'
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = get_keycloak_args()
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/logout?post_logout_redirect_uri={return_redirect_url}&id_token_hint={id_token}"

        return redirect(request_url)

    @staticmethod
    def generate_state():
        rando = random.randbytes(24)
        state = base64.b64encode(bytes(rando))
        print("generate_state")
        return state

    def get_login_redirect_url(self, state):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = get_keycloak_args()
        return_redirect_url = 'http://localhost:7000/v1.0/login_return'
        login_redirect_url = f'{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/auth?' + \
                       f'state={state}&' + \
                       'response_type=code&' + \
                       f'client_id={keycloak_client_id}&' + \
                       'scope=openid&' + \
                       f'redirect_uri={return_redirect_url}'
        return login_redirect_url

    def get_id_token_object(self, code):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = get_keycloak_args()

        BACKEND_BASIC_AUTH_STRING = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        BACKEND_BASIC_AUTH_BYTES = bytes(BACKEND_BASIC_AUTH_STRING, encoding='ascii')
        BACKEND_BASIC_AUTH = base64.b64encode(BACKEND_BASIC_AUTH_BYTES)
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": f"Basic {BACKEND_BASIC_AUTH.decode('utf-8')}"}

        data = {'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:7000/v1.0/login_return'}

        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"

        response = requests.post(request_url, data=data, headers=headers)
        id_token_object = json.loads(response.text)
        return id_token_object

    @staticmethod
    def validate_id_token(id_token):
        now = time.time()
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = get_keycloak_args()
        try:
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        except Exception as e:
            raise ApiError(code='bad_id_token',
                           message="Cannot decode id_token",
                           status_code=401)
        try:
            assert decoded_token['iss'] == f"{keycloak_server_url}/realms/{keycloak_realm_name}"
            assert decoded_token['aud'] == keycloak_client_id
            if 'azp' in decoded_token:
                assert decoded_token['azp'] == keycloak_client_id
            assert now > decoded_token['iat']
            assert now < decoded_token['exp']
        except Exception as e:
            current_app.logger.error(f"Exception validating id_token: {e}")
            return False
        return True

    def get_bearer_token_from_internal_token(self, internal_token):
        print(f"get_user_by_internal_token: {internal_token}")

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
        if public_response.status_code == 200:
            public_token = json.loads(public_response.text)
            if 'access_token' in public_token:
                return public_token['access_token']
        raise ApiError(code='no_public_access_token',
                       message=f"We could not get a public access token: {username}")

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
