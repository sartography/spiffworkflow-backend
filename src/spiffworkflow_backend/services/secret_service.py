"""Secret_service."""
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db

from spiffworkflow_backend.models.secret_model import SecretAllowedProcessPathModel
from spiffworkflow_backend.models.secret_model import SecretModel


class SecretService:
    """SecretService."""

    @staticmethod
    def add_secret(
        service: str,
        client: str,
        key: str,
        creator_user_id: int = None,
        allowed_process: str = None,
    ):
        """Add_secret."""
        secret_model = SecretModel(
            service=service, client=client, key=key, creator_user_id=creator_user_id
        )
        db.session.add(secret_model)
        try:
            db.session.commit()
        except Exception as e:
            raise ApiError(
                code="create_secret_failed",
                message=f"Cannot create secret for service: {service} and client: {client}. Original error is {e}",
            ) from e
        return secret_model

    @staticmethod
    def get_secret(service: str, client: str) -> str:
        """Get_secret."""
        secret = (
            db.session.query(SecretModel.key)
            .filter(SecretModel.service == service)
            .filter(SecretModel.client == client)
            .scalar()
        )
        if secret:
            return secret

    @staticmethod
    def add_allowed_process(secret_id: int, allowed_relative_path: str):
        """Add_allowed_process."""
        secret_process_model = SecretAllowedProcessPathModel(
            secret_id=secret_id, allowed_relative_path=allowed_relative_path
        )
        db.session.add(secret_process_model)
        try:
            db.session.commit()
        except Exception as e:
            raise ApiError(
                code="create_allowed_process_failure",
                message=f"Count not create an allowed process for for secret: {secret_id} "
                f"with path: {allowed_relative_path}. "
                f"Original error is {e}",
            ) from e
        return secret_process_model

    def update_secret(
        self,
        service: str,
        client: str,
        secret: str = None,
        creator_user_id: int = None,
        allowed_process: str = None,
    ):
        """Does this pass pre commit?"""
        ...

    def delete_secret(self, service: str, client: str):
        """Delete secret."""
        ...
