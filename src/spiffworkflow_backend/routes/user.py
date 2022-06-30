"""User."""
from flask_bpmn.api.api_error import ApiError
from typing import Dict
from typing import Optional

from flask import g

from spiffworkflow_backend.models.user import UserModel

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
    failure_error = ApiError(
        "invalid_token",
        "Unable to decode the token you provided.  Please re-authenticate",
        status_code=403,
    )

    if token:
        try:
            token_info = UserModel.decode_auth_token(token)
            g.user = UserModel.query.filter_by(uid=token_info["sub"]).first()

            # If the user is valid, store the token for this session
            if g.user:
                g.token = token
        except Exception:
            raise failure_error
        if g.user is not None:
            return token_info
        else:
            raise failure_error

    else:
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
