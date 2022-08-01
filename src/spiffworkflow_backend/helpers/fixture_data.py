"""Fixture_data."""
from typing import Any

from flask_bpmn.models.db import db
from sqlalchemy.exc import IntegrityError

from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.user_service import UserService


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()

    if user is None:
        user = UserService().create_user('local', username, username=username)
        principal = UserService().create_principal(user_id=user.id)

    return user
