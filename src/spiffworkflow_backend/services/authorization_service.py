"""Authorization_service."""
import base64
import json
from typing import Union

import jwt
import requests
from flask import current_app
from flask_bpmn.api.api_error import ApiError


class AuthorizationService:
    """Determine whether a user has permission to perform their request."""

    @staticmethod
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

    def get_user_info_from_id_token(self, token: str) -> dict:
        """This seems to work with basic tokens too."""
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = AuthorizationService.get_keycloak_args()

        # backend_basic_auth_string = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        # backend_basic_auth_bytes = bytes(backend_basic_auth_string, encoding="ascii")
        # backend_basic_auth = base64.b64encode(backend_basic_auth_bytes)

        headers = {"Authorization": f"Bearer {token}"}

        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/userinfo"
        try:
            request_response = requests.get(request_url, headers=headers)
        except Exception as e:
            current_app.logger.error(f"Exception in get_user_info_from_id_token: {e}")
            raise ApiError(
                code="token_error",
                message=f"Exception in get_user_info_from_id_token: {e}",
                status_code=401,
            ) from e

        if request_response.status_code == 401:
            raise ApiError(
                code="invalid_token", message="Please login", status_code=401
            )
        elif request_response.status_code == 200:
            user_info: dict = json.loads(request_response.text)
            return user_info

        raise ApiError(
            code="user_info_error",
            message="Cannot get user info in get_user_info_from_id_token",
            status_code=401,
        )

    # def refresh_token(self, token: str) -> str:
    #     """Refresh_token."""
    #     # if isinstance(token, str):
    #     #     token = eval(token)
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #     headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
    #     data = {
    #         "grant_type": "refresh_token",
    #         "client_id": "spiffworkflow-frontend",
    #         "subject_token": token,
    #         "refresh_token": token,
    #     }
    #     refresh_response = requests.post(request_url, headers=headers, data=data)
    #     refresh_token = json.loads(refresh_response.text)
    #     return refresh_token

    def get_bearer_token(self, basic_token: str) -> dict:
        """Get_bearer_token."""
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = AuthorizationService.get_keycloak_args()

        backend_basic_auth_string = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        backend_basic_auth_bytes = bytes(backend_basic_auth_string, encoding="ascii")
        backend_basic_auth = base64.b64encode(backend_basic_auth_bytes)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {backend_basic_auth.decode('utf-8')}",
        }
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": keycloak_client_id,
            "subject_token": basic_token,
            "audience": keycloak_client_id,
        }
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"

        backend_response = requests.post(request_url, headers=headers, data=data)
        # json_data = json.loads(backend_response.text)
        # bearer_token = json_data['access_token']
        bearer_token: dict = json.loads(backend_response.text)
        return bearer_token

    @staticmethod
    def decode_auth_token(auth_token: str) -> dict[str, Union[str, None]]:
        """Decode the auth token.

        :param auth_token:
        :return: integer|string
        """
        secret_key = current_app.config.get("SECRET_KEY")
        if secret_key is None:
            raise KeyError("we need current_app.config to have a SECRET_KEY")

        try:
            payload = jwt.decode(auth_token, options={"verify_signature": False})
            return payload
        except jwt.ExpiredSignatureError as exception:
            raise ApiError(
                "token_expired",
                "The Authentication token you provided expired and must be renewed.",
            ) from exception
        except jwt.InvalidTokenError as exception:
            raise ApiError(
                "token_invalid",
                "The Authentication token you provided is invalid. You need a new token. ",
            ) from exception

    # def get_bearer_token_from_internal_token(self, internal_token):
    #     """Get_bearer_token_from_internal_token."""
    #     self.decode_auth_token(internal_token)
    #     print(f"get_user_by_internal_token: {internal_token}")

    # def introspect_token(self, basic_token: str) -> dict:
    #     """Introspect_token."""
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #
    #     bearer_token = AuthorizationService().get_bearer_token(basic_token)
    #     auth_bearer_string = f"Bearer {bearer_token['access_token']}"
    #
    #     headers = {
    #         "Content-Type": "application/x-www-form-urlencoded",
    #         "Authorization": auth_bearer_string,
    #     }
    #     data = {
    #         "client_id": keycloak_client_id,
    #         "client_secret": keycloak_client_secret_key,
    #         "token": basic_token,
    #     }
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token/introspect"
    #
    #     introspect_response = requests.post(request_url, headers=headers, data=data)
    #     introspection = json.loads(introspect_response.text)
    #
    #     return introspection

    # def get_permission_by_basic_token(self, basic_token: dict) -> list:
    #     """Get_permission_by_basic_token."""
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #
    #     # basic_token = AuthorizationService().refresh_token(basic_token)
    #     # bearer_token = AuthorizationService().get_bearer_token(basic_token['access_token'])
    #     bearer_token = AuthorizationService().get_bearer_token(basic_token)
    #     # auth_bearer_string = f"Bearer {bearer_token['access_token']}"
    #     auth_bearer_string = f"Bearer {bearer_token}"
    #
    #     headers = {
    #         "Content-Type": "application/x-www-form-urlencoded",
    #         "Authorization": auth_bearer_string,
    #     }
    #     data = {
    #         "client_id": keycloak_client_id,
    #         "client_secret": keycloak_client_secret_key,
    #         "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
    #         "response_mode": "permissions",
    #         "audience": keycloak_client_id,
    #         "response_include_resource_name": True,
    #     }
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
    #     permission_response = requests.post(request_url, headers=headers, data=data)
    #     permission = json.loads(permission_response.text)
    #     return permission

    # def get_auth_status_for_resource_and_scope_by_token(
    #     self, basic_token: dict, resource: str, scope: str
    # ) -> str:
    #     """Get_auth_status_for_resource_and_scope_by_token."""
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #
    #     # basic_token = AuthorizationService().refresh_token(basic_token)
    #     bearer_token = AuthorizationService().get_bearer_token(basic_token)
    #     auth_bearer_string = f"Bearer {bearer_token['access_token']}"
    #
    #     headers = {
    #         "Content-Type": "application/x-www-form-urlencoded",
    #         "Authorization": auth_bearer_string,
    #     }
    #     data = {
    #         "client_id": keycloak_client_id,
    #         "client_secret": keycloak_client_secret_key,
    #         "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
    #         "permission": f"{resource}#{scope}",
    #         "response_mode": "permissions",
    #         "audience": keycloak_client_id,
    #     }
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
    #     auth_response = requests.post(request_url, headers=headers, data=data)
    #
    #     print("get_auth_status_for_resource_and_scope_by_token")
    #     auth_status: str = json.loads(auth_response.text)
    #     return auth_status

    # def get_permissions_by_token_for_resource_and_scope(
    #     self, basic_token: str, resource: str|None=None, scope: str|None=None
    # ) -> str:
    #     """Get_permissions_by_token_for_resource_and_scope."""
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #
    #     # basic_token = AuthorizationService().refresh_token(basic_token)
    #     # bearer_token = AuthorizationService().get_bearer_token(basic_token['access_token'])
    #     bearer_token = AuthorizationService().get_bearer_token(basic_token)
    #     auth_bearer_string = f"Bearer {bearer_token['access_token']}"
    #
    #     headers = {
    #         "Content-Type": "application/x-www-form-urlencoded",
    #         "Authorization": auth_bearer_string,
    #     }
    #     permision = ""
    #     if resource is not None and resource != '':
    #         permision += resource
    #     if scope is not None and scope != '':
    #         permision += "#" + scope
    #     data = {
    #         "client_id": keycloak_client_id,
    #         "client_secret": keycloak_client_secret_key,
    #         "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
    #         "response_mode": "permissions",
    #         "permission": permision,
    #         "audience": keycloak_client_id,
    #         "response_include_resource_name": True,
    #     }
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
    #     permission_response = requests.post(request_url, headers=headers, data=data)
    #     permission: str = json.loads(permission_response.text)
    #     return permission

    # def get_resource_set(self, public_access_token, uri):
    #     """Get_resource_set."""
    #     (
    #         keycloak_server_url,
    #         keycloak_client_id,
    #         keycloak_realm_name,
    #         keycloak_client_secret_key,
    #     ) = AuthorizationService.get_keycloak_args()
    #     bearer_token = AuthorizationService().get_bearer_token(public_access_token)
    #     auth_bearer_string = f"Bearer {bearer_token['access_token']}"
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": auth_bearer_string,
    #     }
    #     data = {
    #         "matchingUri": "true",
    #         "deep": "true",
    #         "max": "-1",
    #         "exactName": "false",
    #         "uri": uri,
    #     }
    #
    #     # f"matchingUri=true&deep=true&max=-1&exactName=false&uri={URI_TO_TEST_AGAINST}"
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/authz/protection/resource_set"
    #     response = requests.get(request_url, headers=headers, data=data)
    #
    #     print("get_resource_set")

    def get_permission_by_token(self, public_access_token: str) -> dict:
        """Get_permission_by_token."""
        # TODO: Write a test for this
        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = AuthorizationService.get_keycloak_args()
        bearer_token = AuthorizationService().get_bearer_token(public_access_token)
        auth_bearer_string = f"Bearer {bearer_token['access_token']}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": auth_bearer_string,
        }
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "audience": keycloak_client_id,
        }
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        permission_response = requests.post(request_url, headers=headers, data=data)
        permission: dict = json.loads(permission_response.text)

        return permission


class KeycloakAuthorization:
    """Interface with Keycloak server."""


# class KeycloakClient:
