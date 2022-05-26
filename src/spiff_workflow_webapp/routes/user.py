"""User."""
from flask import current_app, g

from flask_bpmn.api.api_error import ApiError
from spiff_workflow_webapp.models.user import UserModel

"""
.. module:: crc.api.user
   :synopsis: Single Sign On (SSO) user login and session handlers
"""


def verify_token(token=None):
    """
        Verifies the token for the user (if provided). If in production environment and token is not provided,
        gets user from the SSO headers and returns their token.

        Args:
            token: Optional[str]

        Returns:
            token: str

        Raises:
            ApiError.  If not on production and token is not valid, returns an 'invalid_token' 403 error.
            If on production and user is not authenticated, returns a 'no_user' 403 error.
   """
    failure_error = ApiError("invalid_token", "Unable to decode the token you provided.  Please re-authenticate",
                             status_code=403)

    if token:
        try:
            token_info = UserModel.decode_auth_token(token)
            g.user = UserModel.query.filter_by(uid=token_info['sub']).first()

            # If the user is valid, store the token for this session
            if g.user:
                g.token = token
        except:
            raise failure_error
        if g.user is not None:
            return token_info
        else:
            raise failure_error

    # If there's no token and we're in production, get the user from the SSO headers and return their token
    elif _is_production():
        uid = "TEST_UID"

        if uid is not None:
            db_user = UserModel.query.filter_by(uid=uid).first()

            # If the user is valid, store the user and token for this session
            if db_user is not None:
                g.user = db_user
                token = g.user.encode_auth_token()
                g.token = token
                token_info = UserModel.decode_auth_token(token)
                return token_info

            else:
                raise ApiError("no_user",
                               "User not found. Please login via the frontend app before accessing this feature.",
                               status_code=403)

    else:
        # Fall back to a default user if this is not production.
        g.user = UserModel.query.first()
        if not g.user:
            raise ApiError(
                "no_user", "You are in development mode, but there are no users in the database.  Add one, and it will use it.")
        token = g.user.encode_auth_token()
        token_info = UserModel.decode_auth_token(token)
        return token_info


def _is_production():
    """_is_production."""
    return 'PRODUCTION' in current_app.config and current_app.config['PRODUCTION']
