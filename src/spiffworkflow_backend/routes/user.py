"""User."""
import base64
from typing import Dict
from typing import Optional

import jwt
from flask import current_app
from flask import g
from flask import redirect
from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.authentication_service import (
    PublicAuthenticationService,
)
from spiffworkflow_backend.services.authorization_service import AuthorizationService
from spiffworkflow_backend.services.user_service import UserService

"""
.. module:: crc.api.user
   :synopsis: Single Sign On (SSO) user login and session handlers
"""


def verify_token(token: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Verify the token for the user (if provided).

    If in production environment and token is not provided, gets user from the SSO headers and returns their token.

    Args:
        token: Optional[str]

    Returns:
        token: str

    Raises:  # noqa: DAR401
        ApiError:  If not on production and token is not valid, returns an 'invalid_token' 403 error.
        If on production and user is not authenticated, returns a 'no_user' 403 error.
    """
    if token:
        user_info = None

        token_type = get_token_type(token)
        if token_type == "id_token":
            try:
                user_info = AuthorizationService().get_user_info_from_id_token(token)
            except ApiError as ae:
                raise ae
            except Exception as e:
                current_app.logger.error(f"Exception raised in get_token: {e}")
                raise ApiError(
                    code="fail_get_user_info", message="Cannot get user info from token"
                )

        if user_info and "error" not in user_info:  # not sure what to test yet
            user_model = (
                UserModel.query.filter(UserModel.service == "keycloak")
                .filter(UserModel.service_id == user_info["sub"])
                .first()
            )
            if user_model is None:
                # Do we ever get here any more, now that we have login_return method?
                current_app.logger.debug("create_user in verify_token")
                user_model = UserService().create_user(
                    service="keycloak",
                    service_id=user_info["sub"],
                    name=user_info["name"],
                    username=user_info["preferred_username"],
                    email=user_info["email"],
                )
            if user_model:
                g.user = user_model

            # If the user is valid, store the token for this session
            if g.user:
                g.token = token
                scope = get_scope(token)
                return {"uid": g.user.id, "sub": g.user.id, "scope": scope}
                # return validate_scope(token, user_info, user_model)
            else:
                raise ApiError(code="no_user_id", message="Cannot get a user id")

        # no user_info
        else:
            raise ApiError(code="no_user_info", message="Cannot retrieve user info")

    # no token -- do we ever get here?
    else:
        if app.config.get("DEVELOPMENT"):
            # Fall back to a default user if this is not production.
            g.user = UserModel.query.first()
            if not g.user:
                raise ApiError(
                    "no_user",
                    "You are in development mode, but there are no users in the database.  Add one, and it will use it.",
                )
            token_from_user = g.user.encode_auth_token()
            token_info = UserModel.decode_auth_token(token_from_user)
            return token_info

        else:
            raise ApiError(
                code="no_auth_token",
                message="No authorization token was available.",
                status_code=401,
            )


def validate_scope(token) -> bool:
    """Validate_scope."""
    print("validate_scope")
    # token = AuthorizationService().refresh_token(token)
    # user_info = AuthorizationService().get_user_info_from_public_access_token(token)
    # bearer_token = AuthorizationService().get_bearer_token(token)
    # permission = AuthorizationService().get_permission_by_basic_token(token)
    # permissions = AuthorizationService().get_permissions_by_token_for_resource_and_scope(token)
    # introspection = AuthorizationService().introspect_token(basic_token)
    return True


def api_login(uid, password, redirect_url=None):
    """Api_login."""
    token = PublicAuthenticationService().get_public_access_token(uid, password)
    g.token = token

    return token


def encode_auth_token(uid):
    """
    Generates the Auth Token
    :return: string
    """
    payload = {"sub": uid}
    return jwt.encode(
        payload,
        app.config.get("SECRET_KEY"),
        algorithm="HS256",
    )


def login(redirect_url="/"):
    """Login."""
    state = PublicAuthenticationService.generate_state(redirect_url)
    login_redirect_url = PublicAuthenticationService().get_login_redirect_url(state)
    return redirect(login_redirect_url)


def login_return(code, state, session_state):
    """"""
    # TODO: Why does state look like this?
    #  'b\'eydyZWRpcmVjdF91cmwnOiAnaHR0cDovL2xvY2FsaG9zdDo3MDAxLyd9\''
    #  It has an extra 'b at the beginning and an extra ' at the end,
    #  so we use state[2:-1]
    state_dict = eval(base64.b64decode(state[2:-1]).decode("utf-8"))
    state_redirect_url = state_dict["redirect_url"]

    id_token_object = PublicAuthenticationService().get_id_token_object(code)
    id_token = id_token_object["id_token"]

    if PublicAuthenticationService.validate_id_token(id_token):
        user_info = AuthorizationService().get_user_info_from_id_token(
            id_token_object["access_token"]
        )
        if user_info and "error" not in user_info:
            user_model = (
                UserModel.query.filter(UserModel.service == "keycloak")
                .filter(UserModel.service_id == user_info["sub"])
                .first()
            )
            if user_model is None:
                current_app.logger.debug("create_user in login_return")
                name = username = email = ""
                if "name" in user_info:
                    name = user_info["name"]
                if "username" in user_info:
                    username = user_info["username"]
                if "email" in user_info:
                    email = user_info["email"]
                user_model = UserService().create_user(
                    service="keycloak",
                    service_id=user_info["sub"],
                    name=name,
                    username=username,
                    email=email,
                )

            if user_model:
                g.user = user_model.id

            redirect_url = (
                f"{state_redirect_url}?"
                + f"access_token={id_token_object['access_token']}&"
                + f"id_token={id_token}"
            )
            return redirect(redirect_url)

            # return f"{code} {state} {id_token}"


def logout(id_token: str, redirect_url: str | None):
    """Logout."""
    return PublicAuthenticationService().logout(
        id_token=id_token, redirect_url=redirect_url
    )


def logout_return():
    """Logout_return."""
    return redirect(f"http://localhost:7001/")


def get_token_type(token) -> bool:
    """Get_token_type."""
    token_type = None
    try:
        PublicAuthenticationService.validate_id_token(token)
    except ApiError as ae:
        if ae.status_code == 401:
            raise ae
        print(f"ApiError in get_token_type: {ae}")
    except Exception as e:
        print(f"Exception in get_token_type: {e}")
    else:
        token_type = "id_token"
    # try:
    #     # see if we have an open_id token
    #     decoded_token = AuthorizationService.decode_auth_token(token)
    # else:
    #     if 'sub' in decoded_token and 'iss' in decoded_token and 'aud' in decoded_token:
    #         token_type = 'id_token'

    # if 'token_type' in decoded_token and 'sub' in decoded_token:
    #     return True
    return token_type


def get_scope(token):
    """Get_scope."""
    decoded_token = jwt.decode(token, options={"verify_signature": False})
    scope = decoded_token["scope"]
    return scope
