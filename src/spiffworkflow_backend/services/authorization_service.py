"""Authorization_service."""
import requests
import base64
import json
import enum
from flask import g
from flask import current_app


class AuthorizationService:
    """Determine whether a user has permission to perform their request."""
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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()
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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

        bearer_token = AuthorizationService().get_bearer_token(basic_token)
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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

        # basic_token = AuthorizationService().refresh_token(basic_token)
        # bearer_token = AuthorizationService().get_bearer_token(basic_token['access_token'])
        bearer_token = AuthorizationService().get_bearer_token(basic_token)
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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

        # basic_token = AuthorizationService().refresh_token(basic_token)
        bearer_token = AuthorizationService().get_bearer_token(basic_token)
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
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = AuthorizationService.get_keycloak_args()

        # basic_token = AuthorizationService().refresh_token(basic_token)
        # bearer_token = AuthorizationService().get_bearer_token(basic_token['access_token'])
        bearer_token = AuthorizationService().get_bearer_token(basic_token)
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


class KeycloakAuthorization:
    """Interface with Keycloak server."""
