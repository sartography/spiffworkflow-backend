"""Fixture_data."""
from typing import Any

from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.user_service import UserService


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()

    if user is None:
        user = UserService().create_user("local", username, username=username)
        UserService().create_principal(user_id=user.id)

    return user
