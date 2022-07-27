"""Fixture_data."""
from typing import Any

from flask_bpmn.models.db import db
from sqlalchemy.exc import IntegrityError

from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.user import UserModel


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username,
                         service='local',
                         service_id=username)
        db.session.add(user)
        db.session.commit()

    principal = PrincipalModel.query.filter_by(user_id=user.id).first()
    if principal is None:
        principal = PrincipalModel(user_id=user.id)
        db.session.add(principal)
        try:
            db.session.commit()
        except IntegrityError:
            # we just want it to exist. if it was inserted by another process, that's cool
            pass

    return user
