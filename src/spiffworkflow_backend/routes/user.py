"""User."""
import jwt

from typing import Dict
from typing import Optional

from flask import g
from flask import current_app
from flask.app import Flask
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db


from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.authentication_service import AuthenticationService, PublicAuthenticationService

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
    # failure_error = ApiError(
    #     "invalid_token",
    #     "Unable to decode the token you provided.  Please re-authenticate",
    #     status_code=403,
    # )

    if token:
        # maybe need to refresh the token?
        # token = AuthenticationService().refresh_token(token)
        # bearer_token = AuthenticationService().get_bearer_token(token)
        # if bearer_token:  # not sure what to test yet...
        try:
            user_info = AuthenticationService().get_user_info_from_public_access_token(token)
        except Exception as e:
            raise ApiError(code="fail_get_user_info",
                           message="Cannot get user info from token")
        if user_info:  # not sure what to test yet
            user_model = UserModel.query.filter(UserModel.service == 'keycloak').filter(UserModel.service_id==user_info['sub']).first()
            if user_model is None:
                user_model = UserModel(service='keycloak',
                                       service_id=user_info['sub'],
                                       name=user_info['preferred_username'],
                                       username=user_info['sub'])
                db.session.add(user_model)
                db.session.commit()
            g.user = user_model.id
            # If the user is valid, store the token for this session
            if g.user:
                g.token = token
                # What should we return? Dict?
                return user_info
            else:
                raise ApiError(code="no_user_id",
                               message="Cannot get a user id")

        # no user_info
        else:
            raise ApiError(code="no_user_info",
                           message="Cannot retrieve user info")

            # token_info = UserModel.decode_auth_token(token)
            # g.user = UserModel.query.filter_by(uid=token_info["sub"]).first()
            # user_model = UserModel.query.filter(UserModel.username == user_info.id)

            # If the user is valid, store the token for this session
            # if g.user:
            #     g.token = bearer_token
            #     return g.token
            # else:
            #     raise failure_error
            # except Exception:
            #     raise failure_error
            # if g.user is not None:
            #     return g.token
            # validate_scope(g.token)
        # else:
        #     raise ApiError(code="no_bearer_token",
        #                    message="Cannot get Bearer token")

    else:
        if app.config.get('DEVELOPMENT'):
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
            raise ApiError(code="no_auth_token",
                           message="No authorization token was available.",
                           status_code=401)

def validate_scope(token):
    print("validate_scope")
    return True


def api_login(uid, password, redirect_url=None):

    # keycloak_server_url = current_app.config['KEYCLOAK_SERVER_URL']
    # # keycloak_client_id = current_app.config["KEYCLOAK_CLIENT_ID"]
    # keycloak_client_id = 'spiffworkflow-frontend'
    # keycloak_realm_name = current_app.config["KEYCLOAK_REALM_NAME"]
    # keycloak_client_secret_key = current_app.config["KEYCLOAK_CLIENT_SECRET_KEY"]  # noqa: S105
    #
    # keycloak_openid = AuthenticationService.get_keycloak_openid(
    #     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
    # )
    # token = AuthenticationService.get_keycloak_token(keycloak_openid, uid, password)
    token = PublicAuthenticationService().get_public_access_token(uid, password)
    print(f"api_login")
    g.token = token
    # return token['access_token']
    # return encode_auth_token(uid)
    return token

def encode_auth_token(uid):
    """
    Generates the Auth Token
    :return: string
    """
    payload = {
        'sub': uid
    }
    return jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256',
    )

