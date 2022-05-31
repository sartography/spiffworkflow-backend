"""User."""
import jwt
import marshmallow
from flask import current_app
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db
from marshmallow import Schema
from sqlalchemy.orm import relationship  # type: ignore

from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user_group_assignment import UserGroupAssignmentModel


class UserModel(db.Model):  # type: ignore
    """UserModel."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    uid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    user_group_assignments = relationship(UserGroupAssignmentModel, cascade="delete")
    groups = relationship(
        GroupModel,
        viewonly=True,
        secondary="user_group_assignment",
        overlaps="user_group_assignments,users",
    )

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        # hours = float(app.config['TOKEN_AUTH_TTL_HOURS'])
        payload = {
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours, minutes=0, seconds=0),
            # 'iat': datetime.datetime.utcnow(),
            "sub": self.uid
        }
        return jwt.encode(
            payload,
            current_app.config.get("SECRET_KEY"),
            algorithm="HS256",
        )

    def is_admin(self):
        """Is_admin."""
        return True

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get("SECRET_KEY"), algorithms="HS256"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ApiError(
                "token_expired",
                "The Authentication token you provided expired and must be renewed.",
            )
        except jwt.InvalidTokenError:
            raise ApiError(
                "token_invalid",
                "The Authentication token you provided is invalid. You need a new token. ",
            )


class UserModelSchema(Schema):
    """UserModelSchema."""

    class Meta:
        """Meta."""

        model = UserModel
        # load_instance = True
        # include_relationships = False
        # exclude = ("UserGroupAssignment",)

    id = marshmallow.fields.String(required=True)
    username = marshmallow.fields.String(required=True)


class AdminSessionModel(db.Model):
    """AdminSessionModel."""

    __tablename__ = "admin_session"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True)
    admin_impersonate_uid = db.Column(db.String(50))
