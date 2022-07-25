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

class AuthenticationServiceProviders(enum.Enum):
    keycloak = 'keycloak'
    internal = 'internal'


class PublicAuthenticationService:
    """Not sure where/if this ultimately lives.
    It uses a separate public keycloak client: spiffworkflow-frontend
    """
    def get_public_access_token(self, username, password) -> dict:
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()
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

    @staticmethod
    def get_keycloak_args():
        keycloak_server_url = current_app.config['KEYCLOAK_SERVER_URL']
        keycloak_client_id = current_app.config["KEYCLOAK_CLIENT_ID"]
        keycloak_realm_name = current_app.config["KEYCLOAK_REALM_NAME"]
        keycloak_client_secret_key = current_app.config["KEYCLOAK_CLIENT_SECRET_KEY"]  # noqa: S105
        return keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key

    def get_user_info_from_public_access_token(self, public_access_token):
        """This seems to work with basic tokens too"""
        json_data = None
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        bearer_token = self.get_bearer_token(public_access_token)
        auth_bearer_string = f"Bearer {bearer_token['access_token']}"
        # auth_bearer_string = f"Bearer {public_access_token}"
        headers = {"Content-Type": "application/json",
                   "Authorization": auth_bearer_string}
        data = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'client_id': keycloak_client_id,
                # "subject_token": bearer_token['access_token'],
                "subject_token": public_access_token,
                "audience": keycloak_client_id}

        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/userinfo"
        try:
            request_response = requests.post(request_url, headers=headers, data=data)
        except Exception as e:
            print(f"get_user_from_token: Exeption: {e}")
        else:
            print("else")
            json_data = json.loads(request_response.text)
        return json_data

    def refresh_token(self, basic_token):
        # if isinstance(basic_token, str):
        #     basic_token = eval(basic_token)
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        data = {'grant_type': 'refresh_token',
                'client_id': 'spiffworkflow-frontend',
                'subject_token': basic_token,
                'refresh_token': basic_token}
        refresh_response = requests.post(request_url, headers=headers, data=data)
        refresh_token = json.loads(refresh_response.text)
        return refresh_token

    def get_bearer_token(self, basic_token):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        BACKEND_BASIC_AUTH_STRING = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        BACKEND_BASIC_AUTH_BYTES = bytes(BACKEND_BASIC_AUTH_STRING, encoding='ascii')
        BACKEND_BASIC_AUTH = base64.b64encode(BACKEND_BASIC_AUTH_BYTES)

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": f"Basic {BACKEND_BASIC_AUTH.decode('utf-8')}"}
        data = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'client_id': keycloak_client_id,
                "subject_token": basic_token,
                "audience": keycloak_client_id}
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"

        backend_response = requests.post(request_url, headers=headers, data=data)
        # json_data = json.loads(backend_response.text)
        # bearer_token = json_data['access_token']
        bearer_token = json.loads(backend_response.text)
        return bearer_token

    def introspect_token(self, basic_token):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        bearer_token = AuthenticationService().get_bearer_token(basic_token)
        auth_bearer_string = f"Bearer {bearer_token['access_token']}"

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": auth_bearer_string}
        data = {'client_id': keycloak_client_id,
                'client_secret': keycloak_client_secret_key,
                'token': basic_token}
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token/introspect"

        introspect_response = requests.post(request_url, headers=headers, data=data)
        introspection = json.loads(introspect_response.text)

        return introspection

    def get_permission_by_basic_token(self, basic_token):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        # basic_token = AuthenticationService().refresh_token(basic_token)
        # bearer_token = AuthenticationService().get_bearer_token(basic_token['access_token'])
        bearer_token = AuthenticationService().get_bearer_token(basic_token)
        # auth_bearer_string = f"Bearer {bearer_token['access_token']}"
        auth_bearer_string = f"Bearer {bearer_token}"

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": auth_bearer_string}
        data = {'client_id': keycloak_client_id,
                'client_secret': keycloak_client_secret_key,
                "grant_type": 'urn:ietf:params:oauth:grant-type:uma-ticket',
                "response_mode": "permissions",
                "audience": keycloak_client_id
        }
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        permission_response = requests.post(request_url, headers=headers, data=data)
        permission = json.loads(permission_response.text)
        return permission

    def get_auth_status_for_resource_and_scope_by_token(self, basic_token, resource, scope):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        # basic_token = AuthenticationService().refresh_token(basic_token)
        bearer_token = AuthenticationService().get_bearer_token(basic_token)
        auth_bearer_string = f"Bearer {bearer_token['access_token']}"

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": auth_bearer_string}
        data = {
            'client_id': keycloak_client_id,
            'client_secret': keycloak_client_secret_key,
            "grant_type": 'urn:ietf:params:oauth:grant-type:uma-ticket',
            "permission": f"{resource}#{scope}",
            "response_mode": "permissions",
            "audience": keycloak_client_id
        }
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        auth_response = requests.post(request_url, headers=headers, data=data)

        print("get_auth_status_for_resource_and_scope_by_token")
        auth_status = json.loads(auth_response.text)
        return auth_status

    def get_permissions_by_token_for_resource_and_scope(self, basic_token, resource, scope):
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthenticationService.get_keycloak_args()

        # basic_token = AuthenticationService().refresh_token(basic_token)
        # bearer_token = AuthenticationService().get_bearer_token(basic_token['access_token'])
        bearer_token = AuthenticationService().get_bearer_token(basic_token)
        auth_bearer_string = f"Bearer {bearer_token['access_token']}"

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": auth_bearer_string}
        data = {'client_id': keycloak_client_id,
                'client_secret': keycloak_client_secret_key,
                "grant_type": 'urn:ietf:params:oauth:grant-type:uma-ticket',
                "response_mode": "permissions",
                "permission": f"{resource}#{scope}",
                "audience": keycloak_client_id
        }
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        permission_response = requests.post(request_url, headers=headers, data=data)
        permission = json.loads(permission_response.text)
        return permission



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