"""Fixture_data."""
from typing import Any

from flask_bpmn.models.db import db

from spiffworkflow_backend.models.user import UserModel


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username)
        db.session.add(user)
        db.session.commit()

    return user
