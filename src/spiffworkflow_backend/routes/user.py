"""User."""
import jwt
import requests
import json
from urllib.parse import urlencode, quote
import base64

from typing import Dict
from typing import Optional

from flask import g
from flask import current_app
from flask import redirect
from flask import request
from flask.app import Flask
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db


from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.authentication_service import PublicAuthenticationService, get_keycloak_args
from spiffworkflow_backend.services.authorization_service import AuthorizationService

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

    # bearer_token = AuthorizationService().get_bearer_token(token)
    # token = AuthorizationService().refresh_token(token)
    # maybe need to refresh the token?

    if token:
        if is_internal_token(token):
            try:
                PublicAuthenticationService.get_bearer_token_from_internal_token(token)
            except Exception as e:
                current_app.logger.error(f"Exception raised decoding token: {e}")
                raise ApiError(code="fail_decode_auth_token",
                               message="Cannot decode the auth token")

        try:
            user_info = AuthorizationService().get_user_info_from_public_access_token(token)
        except ApiError as ae:
            raise ae
        except Exception as e:
            current_app.logger.error(f"Exception raised in get_token: {e}")
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
                try:
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Exception raised while adding user in get_token: {e}")
                    raise ApiError(code="fail_add_user_model",
                                   message="Cannot add user in verify_token") from e
            if user_model:
                g.user = user_model.id

            # If the user is valid, store the token for this session
            if g.user:
                g.token = token
                # What should we return? Dict?
                # return user_info
                return validate_scope(token, user_info, user_model)
            else:
                raise ApiError(code="no_user_id",
                               message="Cannot get a user id")

        # no user_info
        else:
            raise ApiError(code="no_user_info",
                           message="Cannot retrieve user info")

    # no token -- do we ever get here?
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

def validate_scope(token, user_info, user_model):
    print("validate_scope")
    # token = AuthorizationService().refresh_token(token)
    # user_info = AuthorizationService().get_user_info_from_public_access_token(token)
    # bearer_token = AuthorizationService().get_bearer_token(token)
    # permission = AuthorizationService().get_permission_by_basic_token(token)
    # permissions = AuthorizationService().get_permissions_by_token_for_resource_and_scope(token)
    introspection = AuthorizationService().introspect_token(basic_token)
    return True


def api_login(uid, password, redirect_url=None):

    token = PublicAuthenticationService().get_public_access_token(uid, password)
    g.token = token

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

def login_redirect(redirect_url='/'):
    state = PublicAuthenticationService.generate_state()
    login_redirect_url = PublicAuthenticationService().get_login_redirect_url(state)
    return redirect(login_redirect_url)

def login_return(code, state, session_state):
    """"""

    id_token_object = PublicAuthenticationService().get_id_token_object(code)
    id_token = id_token_object['id_token']

    if PublicAuthenticationService.validate_id_token(id_token):
        user_info = AuthorizationService().get_user_info_from_id_token_object(id_token_object)
        if user_info:
            user_model = UserModel.query.filter(UserModel.service == 'keycloak').filter(UserModel.service_id==user_info['sub']).first()
            if user_model is None:
                user_model = UserModel.from_open_id_user_info(user_info)
                db.session.add(user_model)
                try:
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Exception raised while adding user in get_token: {e}")
                    raise ApiError(code="fail_add_user_model",
                                   message="Cannot add user in verify_token")
            if user_model:
                g.user = user_model.id

            return redirect(f"http://localhost:7001/?access_token={id_token_object['access_token']}&id_token={id_token}")

            # return f"{code} {state} {id_token}"

def logout(id_token: str, redirect_url: str | None):
    return PublicAuthenticationService().logout(id_token=id_token, redirect_url=redirect_url)

def logout_return():
    return redirect(f"http://localhost:7001/")

def is_internal_token(token) -> bool:
    decoded_token = UserModel.decode_auth_token(token)
    print("is_internal_token")
    return True
