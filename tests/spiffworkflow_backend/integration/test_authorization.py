"""Test_authorization."""
import requests  # type: ignore
from flask.app import Flask
from flask.testing import FlaskClient

from tests.spiffworkflow_backend.integration.base_test import BaseTest

from spiffworkflow_backend.services.authorization_service import AuthorizationService

# keycloak_server_url = "http://localhost:7002/"


class TestAuthorization(BaseTest):
    """TestAuthorization."""
    def test_get_bearer_token(self, app: Flask) -> None:
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            public_access_token = self.get_public_access_token(user_id, user_id)
            bearer_token = AuthorizationService().get_bearer_token(public_access_token)
            assert isinstance(public_access_token, str)
            assert isinstance(bearer_token, dict)
            assert 'access_token' in bearer_token
            assert isinstance(bearer_token['access_token'], str)
            assert 'refresh_token' in bearer_token
            assert isinstance(bearer_token['refresh_token'], str)
            assert 'token_type' in bearer_token
            assert bearer_token['token_type'] == 'Bearer'
            assert 'scope' in bearer_token
            assert isinstance(bearer_token['scope'], str)

    def test_get_user_info_from_public_access_token(self, app: Flask) -> None:
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            public_access_token = self.get_public_access_token(user_id, user_id)
            user_info = AuthorizationService().get_user_info_from_public_access_token(public_access_token)
            assert 'sub' in user_info
            assert isinstance(user_info['sub'], str)
            assert len(user_info['sub']) == 36
            assert 'preferred_username' in user_info
            assert user_info['preferred_username'] == user_id
            assert 'email' in user_info
            assert user_info['email'] == f"{user_id}@example.com"

    def test_introspect_token(self, app: Flask) -> None:
        keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            basic_token = self.get_public_access_token(user_id, user_id)
            introspection = AuthorizationService().introspect_token(basic_token)
            assert isinstance(introspection, dict)
            assert introspection['typ'] == 'Bearer'
            assert introspection['preferred_username'] == user_id
            assert introspection['client_id'] == 'spiffworkflow-frontend'

            assert 'resource_access' in introspection
            resource_access = introspection['resource_access']
            assert isinstance(resource_access, dict)

            assert keycloak_client_id in resource_access
            client = resource_access[keycloak_client_id]
            assert 'roles' in client
            roles = client['roles']

            assert isinstance(roles, list)
            if user_id == 'admin_1':
                assert len(roles) == 2
                for role in roles:
                    assert role in ('User', 'Admin')
            elif user_id == 'admin_2':
                assert len(roles) == 1
                assert roles[0] == 'User'
            elif user_id == 'user_1' or user_id == 'user_2':
                assert len(roles) == 2
                for role in roles:
                    assert role in ('User', 'Anonymous')

    def test_get_permission_by_token(self, app: Flask) -> None:
        resource_names = 'Default Resource', 'Process Groups', 'Process Models'
        output = {}
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            output[user_id] = {}
            basic_token = self.get_public_access_token(user_id, user_id)
            permissions = AuthorizationService().get_permission_by_basic_token(basic_token)
            if isinstance(permissions, list):
                for permission in permissions:
                    resource_name = permission['rsname']
                    output[user_id][resource_name] = {}
                    # assert resource_name in resource_names
                    # if resource_name == 'Process Groups' or resource_name == 'Process Models':
                    if 'scopes' in permission:
                        # assert 'scopes' in permission
                        scopes = permission['scopes']
                        output[user_id][resource_name]['scopes'] = scopes
                        # assert isinstance(scopes, list)
                        # assert len(scopes) == 1
                        # assert scopes[0] == 'read'
                    # else:
                    #     # assert 'scopes' not in permission
                    #     ...

                # if user_id == 'admin_1':
                #     # assert len(permissions) == 3
                #     for permission in permissions:
                #         resource_name = permission['rsname']
                #         # assert resource_name in resource_names
                #         if resource_name == 'Process Groups' or resource_name == 'Process Models':
                #             # assert len(permission['scopes']) == 4
                #             for item in permission['scopes']:
                #                 # assert item in ('instantiate', 'read', 'update', 'delete')
                #                 ...
                #         else:
                #             # assert resource_name == 'Default Resource'
                #             # assert 'scopes' not in permission
                #             ...
                #
                # if user_id == 'admin_2':
                #     # assert len(permissions) == 3
                #     for permission in permissions:
                #         resource_name = permission['rsname']
                #         # assert resource_name in resource_names
                #         if resource_name == 'Process Groups' or resource_name == 'Process Models':
                #             # assert len(permission['scopes']) == 1
                #             # assert permission['scopes'][0] == 'read'
                #             ...
                #         else:
                #             # assert resource_name == 'Default Resource'
                #             # assert 'scopes' not in permission
                #             ...
            else:
                print(f"No Permissions: {permissions}")
        print("test_get_permission_by_token")

    def test_get_auth_status_for_resource_and_scope_by_token(self, app: Flask) -> None:
        resources = 'Admin', 'Process Groups', 'Process Models'
        # scope = 'read'
        output = {}
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            output[user_id] = {}
            basic_token = self.get_public_access_token(user_id, user_id)
            for resource in resources:
                output[user_id][resource] = {}
                for scope in 'instantiate', 'read', 'update', 'delete':
                    auth_status = AuthorizationService().get_auth_status_for_resource_and_scope_by_token(
                        basic_token, resource, scope
                    )
                    output[user_id][resource][scope] = auth_status
        print("test_get_auth_status_for_resource_and_scope_by_token")

    def test_get_permissions_by_token_for_resource_and_scope(self, app: Flask):
        resource_names = 'Default Resource', 'Process Groups', 'Process Models'
        output = {}
        for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
            output[user_id] = {}
            basic_token = self.get_public_access_token(user_id, user_id)
            for resource in resource_names:
                output[user_id][resource] = {}
                for scope in 'instantiate', 'read', 'update', 'delete':
                    permissions = AuthorizationService().\
                        get_permissions_by_token_for_resource_and_scope(basic_token, resource, scope)
                    output[user_id][resource][scope] = permissions
        print("test_get_permissions_by_token_for_resource_and_scope")


    # # def test_authorize_action(self, app: Flask, client: FlaskClient) -> None:
    # #     action = 'my_action'
    # #     result = app.get(f'/authorize/{action}')
    # #     print("test_authorize_action")
    #
    # def test_resource_set(self, app: Flask, client: FlaskClient) -> None:
    #     """Test_resource_set."""
    #     # app = app.test_client()
    #     user = 'bob'
    #     password = 'LetMeIn'
    #     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(
    #         app)
    #     keycloak_openid = AuthorizationService.get_keycloak_openid(
    #         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
    #     )
    #     token = keycloak_openid.token(user, password)
    #     # result = requests.get('https://cnn.com')
    #     # payload = {
    #     #     'sub': user
    #     # }
    #     # jwt_header = jwt.encode(
    #     #     payload,
    #     #     token['access_token'],
    #     #     algorithm='HS256',
    #     # )
    #     # headers = {"Authorization": f"Bearer {token['access_token']}"}
    #
    #     headers = dict(Authorization='Bearer ' + token['access_token'])
    #     url = f"http://localhost:8080/realms/{keycloak_realm_name}/protocol/openid-connect/userinfo"
    #     # result = requests.get(url, headers=headers)
    #
    #     url = f"http://127.0.0.1:8080/realms/{keycloak_realm_name}/authz/protection/resource_set?uri=%2Fstatus"
    #     result = requests.get(url, headers=headers)
    #
    #     # result = requests.get(
    #     #     f"http://127.0.0.1:8080/realms/{keycloak_realm_name}/authz/protection/resource_set?matchingUri=true&deep=true&max=-1&exactName=false&uri=%2Fstatus -H Authorization: Bearer {token['access_token']}")
    #     print("test_resource_set")
    # #
    # # curl - k - X
    # # GET
    # # "https://somedomain.test.com/api/Users/Year/2020/Workers?offset=1&limit=100" - H
    # # "accept: application/json" - H
    # # "Authorization: Bearer zz8d62zz-56zz-34zz-9zzf-azze1b8057f8"
    #
    # #
    # # rv = self.app.get('/v1.0/workflow-specification/%s/validate' % spec_model.id, headers=self.logged_in_headers())
    # # cls.app = app.test_client()
    #
    # #   GET /realms/quarkus/authz/protection/resource_set?matchingUri=true&deep=true&max=-1&exactName=false&
    # #   uri=%2Fapi%2Fusers%2Fme HTTP/1.1..Authorization:
    # #   Bearer
    # #   eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjZklBRE5feHhDSm1Wa1d5Ti1QTlhFRXZNVVdzMnI2OEN4dG1oRUROelhVIn0.eyJleHAiOjE2NTcxMzgzNzAsImlhdCI6MTY1NzEzODA3MCwianRpIjoiY2I1OTc0OTAtYzJjMi00YTFkLThkNmQtMzBkOGU5YzE1YTNlIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo0MzI3OS9yZWFsbXMvcXVhcmt1cyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI5NDhjNTllYy00NmVkLTRkOTktYWE0My0wMjkwMDAyOWI5MzAiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJiYWNrZW5kLXNlcnZpY2UiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiXX0sInJlc291cmNlX2FjY2VzcyI6eyJiYWNrZW5kLXNlcnZpY2UiOnsicm9sZXMiOlsidW1hX3Byb3RlY3Rpb24iXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImNsaWVudEhvc3QiOiIxNzIuMTcuMC4xIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJjbGllbnRJZCI6ImJhY2tlbmQtc2VydmljZSIsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1iYWNrZW5kLXNlcnZpY2UiLCJjbGllbnRBZGRyZXNzIjoiMTcyLjE3LjAuMSIsImVtYWlsIjoic2VydmljZS1hY2NvdW50LWJhY2tlbmQtc2VydmljZUBwbGFjZWhvbGRlci5vcmcifQ.VRcdoJQO5KWeDFprl6g21Gp9lAqLH1GUAegZPslI9lcL7wdEDLauleTs7cr9ODvXpBbbWVZirP445H3bIfEpyZ2UiKeoEYB6WvR2r_hIHCbNGrV9klkCVjQSuCtdB-Zf3OWHXctz_warlNXF4i4VLtkettlxeGRTVpqT-_lO-y2PhHVNe7imEcnceoKWZQe-Z0JBAJ1Gs2_mj_vgL8V2ZKAd7x0uuAcNyqo4Kmvqh75vkhIuGYAbWfY--wdv8cuphNpbKCGoz27n-D_Im8tW00B1_twctwXo8yfZHp46o1yERbTCS1Xu_eBFufKB21au6omxneyKSD47AfHLR_ymvg..Host: localhost:43279..Connection: Keep-Alive....  #
