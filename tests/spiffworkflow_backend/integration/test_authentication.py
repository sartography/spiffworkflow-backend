"""Test_authentication."""
from keycloak.authorization import Authorization
from keycloak.keycloak_openid import KeycloakOpenID
from keycloak.uma_permissions import AuthStatus

from spiffworkflow_backend.services.authentication_service import AuthenticationService

server_url = "http://localhost:8080/"
client_id = "bank-api"
realm_name = "stackoverflow-demo"
client_secret_key = "seciKpRanUReL0ksZaFm5nfjhMUKHVAO"

user = "bob"
password = "LetMeIn"

resource = "View Account Resource"
scope = "account:view"


def test_get_keycloak_openid_client():
    """Test_get_keycloak_openid_client."""
    keycloak_openid_client = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    assert isinstance(keycloak_openid_client, KeycloakOpenID)
    assert isinstance(keycloak_openid_client.authorization, Authorization)


def test_get_keycloak_token():
    """Test_get_keycloak_token."""
    keycloak_openid = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    token = keycloak_openid.token(user, password)
    assert isinstance(token, dict)
    assert isinstance(token["access_token"], str)
    assert isinstance(token["refresh_token"], str)
    assert token["expires_in"] == 300
    assert token["refresh_expires_in"] == 1800
    assert token["token_type"] == "Bearer"


def test_get_permission_by_token():
    """Test_get_permission_by_token."""
    keycloak_openid = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    keycloak_openid.load_authorization_config(
        "tests/spiffworkflow_backend/integration/bank-api-authz-config.json"
    )
    token = keycloak_openid.token(user, password)

    AuthenticationService.get_permission_by_token(keycloak_openid, token)
    # TODO: permissions comes back as None. Is this right?
    print("test_get_permission_by_token")


def test_get_uma_permissions_by_token():
    """Test_get_uma_permissions_by_token."""
    keycloak_openid = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    token = keycloak_openid.token(user, password)
    uma_permissions = AuthenticationService.get_uma_permissions_by_token(
        keycloak_openid, token
    )
    assert isinstance(uma_permissions, list)
    assert len(uma_permissions) == 2
    for permission in uma_permissions:
        assert "rsname" in permission
        if permission["rsname"] == "View Account Resource":
            assert "scopes" in permission
            assert isinstance(permission["scopes"], list)
            assert len(permission["scopes"]) == 1
            assert permission["scopes"][0] == "account:view"


def test_get_uma_permissions_by_token_for_resource_and_scope():
    """Test_get_uma_permissions_by_token_for_resource_and_scope."""
    keycloak_openid = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    token = keycloak_openid.token(user, password)
    permissions = (
        AuthenticationService.get_uma_permissions_by_token_for_resource_and_scope(
            keycloak_openid, token, resource, scope
        )
    )
    assert isinstance(permissions, list)
    assert len(permissions) == 1
    assert isinstance(permissions[0], dict)
    permission = permissions[0]
    assert "rsname" in permission
    assert permission["rsname"] == resource
    assert "scopes" in permission
    assert isinstance(permission["scopes"], list)
    assert len(permission["scopes"]) == 1
    assert permission["scopes"][0] == scope


def test_get_auth_status_for_resource_and_scope_by_token():
    """Test_get_auth_status_for_resource_and_scope_by_token."""
    keycloak_openid = AuthenticationService.get_keycloak_openid(
        server_url, client_id, realm_name, client_secret_key
    )
    token = keycloak_openid.token(user, password)
    auth_status = AuthenticationService.get_auth_status_for_resource_and_scope_by_token(
        keycloak_openid, token, resource, scope
    )
    assert isinstance(auth_status, AuthStatus)
    assert auth_status.is_logged_in is True
    assert auth_status.is_authorized is True
