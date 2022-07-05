"""Authentication_service."""
from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin


class AuthenticationService:
    """AuthenticationService."""

    @staticmethod
    def get_keycloak_openid(server_url, client_id, realm_name, client_secret_key):
        keycloak_openid = KeycloakOpenID(server_url=server_url,
                            client_id=client_id,
                            realm_name=realm_name,
                            client_secret_key=client_secret_key)
        return keycloak_openid


    @staticmethod
    def get_keycloak_token(keycloak_openid, user, password):
        token = keycloak_openid.token(user, password)
        return token


    @staticmethod
    def get_permission_by_token(keycloak_openid, token):
        # Get permissions by token
        # KEYCLOAK_PUBLIC_KEY = keycloak_openid.public_key()
        # KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        # policies = keycloak_openid.get_policies(token['access_token'], method_token_info='decode',
        #                                         key=KEYCLOAK_PUBLIC_KEY)
        permissions = keycloak_openid.get_permissions(token['access_token'], method_token_info='introspect')
        # TODO: Not sure if this is good. Permissions comes back as None
        return permissions

    @staticmethod
    def get_uma_permissions_by_token(keycloak_openid, token):
        permissions = keycloak_openid.uma_permissions(token['access_token'])
        return permissions


    @staticmethod
    def get_uma_permissions_by_token_for_resource_and_scope(keycloak_openid, token, resource, scope):
        permissions = keycloak_openid.uma_permissions(token['access_token'], permissions=f"{resource}#{scope}")
        return permissions


    @staticmethod
    def get_auth_status_for_resource_and_scope_by_token(keycloak_openid, token, resource, scope):
        auth_status = keycloak_openid.has_uma_access(token['access_token'], f"{resource}#{scope}")
        return auth_status


    # TODO: Get this to work
    @staticmethod
    def get_keycloak_admin():
        keycloak_admin = KeycloakAdmin(server_url="http://localhost:8080/auth/",
                                       username='admin',
                                       password='admin',
                                       realm_name="stackoverflow-demo",
                                       # user_realm_name="",
                                       # client_secret_key="seciKpRanUReL0ksZaFm5nfjhMUKHVAO",
                                       verify=True)
        return keycloak_admin
