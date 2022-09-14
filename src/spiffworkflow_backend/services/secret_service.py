"""Secret_service."""
from typing import Optional

from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db

from spiffworkflow_backend.models.secret_model import SecretAllowedProcessPathModel
from spiffworkflow_backend.models.secret_model import SecretModel


class SecretService:
    """SecretService."""

    @staticmethod
    def add_secret(
        key: str,
        value: str,
        creator_user_id: Optional[int] = None,
    ) -> SecretModel:
        """Add_secret."""
        secret_model = SecretModel(
            key=key, value=value, creator_user_id=creator_user_id
        )
        db.session.add(secret_model)
        try:
            db.session.commit()
        except Exception as e:
            raise ApiError(
                code="create_secret_error",
                message=f"There was an error creating a secret with key: {key} and value ending with: {value[:-4]}. "
                f"Original error is {e}",
            ) from e
        return secret_model

    @staticmethod
    def get_secret(key: str) -> str | None:
        """Get_secret."""
        secret: SecretModel = (
            db.session.query(SecretModel).filter(SecretModel.key == key).first()
        )
        if secret is not None:
            return secret.value

    @staticmethod
    def add_allowed_process(
        secret_id: int, user_id: str, allowed_relative_path: str
    ) -> SecretAllowedProcessPathModel:
        """Add_allowed_process."""
        creator = SecretModel.query.filter(SecretModel.id == secret_id).first()
        if creator == user_id:
            secret_process_model = SecretAllowedProcessPathModel(
                secret_id=secret_id, allowed_relative_path=allowed_relative_path
            )
            assert secret_process_model  # noqa: S101
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
        else:
            raise ApiError(
                code="create_allowed_process_path_error",
                message=f"User: {user_id} cannot modify the secret with id : {secret_id}",
            )

    def update_secret(
        self,
        key: str,
        value: str,
        creator_user_id: Optional[int] = None,
    ) -> None:
        """Does this pass pre commit?"""
        ...

    @staticmethod
    def delete_secret(key: str) -> None:
        """Delete secret."""
        secret = SecretModel.query.filter(SecretModel.key == key).first()
        db.session.delete(secret)
        try:
            db.session.commit()
        except Exception as e:
            raise ApiError(
                code="delete_secret_error",
                message=f"Could not delete secret with key: {key}. Original error is: {e}",
            ) from e
