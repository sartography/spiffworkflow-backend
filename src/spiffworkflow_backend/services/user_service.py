"""User_service."""
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db

from flask import g

from spiffworkflow_backend.models.user import AdminSessionModel
from spiffworkflow_backend.models.user import UserModel


class UserService:
    """Provides common tools for working with users."""

    # Returns true if the current user is logged in.
    @staticmethod
    def has_user() -> bool:
        """Has_user."""
        return "token" in g and bool(g.token) and "user" in g and bool(g.user)

    # Returns true if the current user is an admin.
    @staticmethod
    def user_is_admin() -> bool:
        """User_is_admin."""
        return UserService.has_user() and g.user.is_admin()

    # Returns true if the current admin user is impersonating another user.
    @staticmethod
    def admin_is_impersonating() -> bool:
        """Admin_is_impersonating."""
        if UserService.user_is_admin():
            admin_session: AdminSessionModel = UserService.get_admin_session()
            return admin_session is not None

        else:
            raise ApiError(
                "unauthorized",
                "You do not have permissions to do this.",
                status_code=403,
            )

    # Returns true if the given user uid is different from the current user's uid.
    @staticmethod
    def is_different_user(uid):
        """Is_different_user."""
        return UserService.has_user() and uid is not None and uid is not g.user.uid

    @staticmethod
    def current_user(allow_admin_impersonate: bool = False) -> UserModel:
        """Current_user."""
        if not UserService.has_user():
            raise ApiError(
                "logged_out", "You are no longer logged in.", status_code=401
            )

        # Admins can pretend to be different users and act on a user's behalf in
        # some circumstances.
        if (
            UserService.user_is_admin()
            and allow_admin_impersonate
            and UserService.admin_is_impersonating()
        ):
            return UserService.get_admin_session_user()
        else:
            return g.user

    # Admins can pretend to be different users and act on a user's behalf in some circumstances.
    # This method allows an admin user to start impersonating another user with the given uid.
    # Stops impersonating if the uid is None or invalid.
    @staticmethod
    def start_impersonating(uid=None):
        """Start_impersonating."""
        if not UserService.has_user():
            raise ApiError(
                "logged_out", "You are no longer logged in.", status_code=401
            )

        if not UserService.user_is_admin():
            raise ApiError(
                "unauthorized",
                "You do not have permissions to do this.",
                status_code=403,
            )

        if uid is None:
            raise ApiError("invalid_uid", "Please provide a valid user uid.")

        if UserService.is_different_user(uid):
            # Impersonate the user if the given uid is valid.
            impersonate_user = (
                db.session.query(UserModel).filter(UserModel.uid == uid).first()
            )

            if impersonate_user is not None:
                g.impersonate_user = impersonate_user

                # Store the uid and user session token.
                db.session.query(AdminSessionModel).filter(
                    AdminSessionModel.token == g.token
                ).delete()
                db.session.add(
                    AdminSessionModel(token=g.token, admin_impersonate_uid=uid)
                )
                db.session.commit()
            else:
                raise ApiError("invalid_uid", "The uid provided is not valid.")

    @staticmethod
    def stop_impersonating():
        """Stop_impersonating."""
        if not UserService.has_user():
            raise ApiError(
                "logged_out", "You are no longer logged in.", status_code=401
            )

        # Clear out the current impersonating user.
        if "impersonate_user" in g:
            del g.impersonate_user

        admin_session: AdminSessionModel = UserService.get_admin_session()
        if admin_session:
            db.session.delete(admin_session)
            db.session.commit()

    @staticmethod
    def in_list(uids, allow_admin_impersonate=False):
        """Returns true if the current user's id is in the given list of ids.

        False if there is no user, or the user is not in the list.
        """
        if (
            UserService.has_user()
        ):  # If someone is logged in, lock tasks that don't belong to them.
            user = UserService.current_user(allow_admin_impersonate)
            if user.uid in uids:
                return True
        return False

    @staticmethod
    def get_admin_session() -> AdminSessionModel:
        """Get_admin_session."""
        if UserService.user_is_admin():
            return (
                db.session.query(AdminSessionModel)
                .filter(AdminSessionModel.token == g.token)
                .first()
            )
        else:
            raise ApiError(
                "unauthorized",
                "You do not have permissions to do this.",
                status_code=403,
            )

    @staticmethod
    def get_admin_session_user() -> UserModel:
        """Get_admin_session_user."""
        if UserService.user_is_admin():
            admin_session = UserService.get_admin_session()

            if admin_session is not None:
                return (
                    db.session.query(UserModel)
                    .filter(UserModel.uid == admin_session.admin_impersonate_uid)
                    .first()
                )
        else:
            raise ApiError(
                "unauthorized",
                "You do not have permissions to do this.",
                status_code=403,
            )
