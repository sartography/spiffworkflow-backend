"""Data_store_service."""
from crc import session
from crc.models.data_store import DataStoreModel
from crc.models.workflow import WorkflowModel
from flask import g
import sqlalchemy
from sqlalchemy import desc
from spiff_workflow_webapp.api.api_error import ApiError
from typing import Any


class DataStoreBase:
    """DataStoreBase."""

    def set_validate_common(
        self, task_id, study_id, workflow_id, script_name, user_id, file_id, *args
    ):
        """Set_validate_common."""
        self.check_args_2(args, script_name)
        key = args[0]
        value = args[1]
        if script_name == "study_data_set":
            record = {
                "task_id": task_id,
                "study_id": study_id,
                "workflow_id": workflow_id,
                key: value,
            }
        elif script_name == "file_data_set":
            record = {
                "task_id": task_id,
                "study_id": study_id,
                "workflow_id": workflow_id,
                "file_id": file_id,
                key: value,
            }
        elif script_name == "user_data_set":
            record = {
                "task_id": task_id,
                "study_id": study_id,
                "workflow_id": workflow_id,
                "user_id": user_id,
                key: value,
            }
        g.validation_data_store.append(record)
        return record

    def get_validate_common(
        self, script_name, study_id=None, user_id=None, file_id=None, *args
    ):
        """This method uses a temporary validation_data_store that is only available for the current validation request.

        This allows us to set data_store values during validation that don't affect the real data_store.
        For data_store `gets`, we first look in the temporary validation_data_store.
        If we don't find an entry in validation_data_store, we look in the real data_store.
        """
        key = args[0]
        if script_name == "study_data_get":
            # If it's in the validation data store, return it
            for record in g.validation_data_store:
                if (
                    "study_id" in record
                    and record["study_id"] == study_id
                    and key in record
                ):
                    return record[key]
            # If not in validation_data_store, look in the actual data_store
            return self.get_data_common(
                study_id, user_id, "study_data_get", file_id, *args
            )
        elif script_name == "file_data_get":
            for record in g.validation_data_store:
                if (
                    "file_id" in record
                    and record["file_id"] == file_id
                    and key in record
                ):
                    return record[key]
            return self.get_data_common(
                study_id, user_id, "file_data_get", file_id, *args
            )
        elif script_name == "user_data_get":
            for record in g.validation_data_store:
                if (
                    "user_id" in record
                    and record["user_id"] == user_id
                    and key in record
                ):
                    return record[key]
            return self.get_data_common(
                study_id, user_id, "user_data_get", file_id, *args
            )

    @staticmethod
    def check_args(args: Any, maxlen: int = 1, script_name: str = "study_data_get") -> None:
        """Check_args."""
        if len(args) < 1 or len(args) > maxlen:
            raise ApiError(
                code="missing_argument",
                message=f"The {script_name} script takes either one or two arguments, "
                f"starting with the key and an optional default",
            )

    @staticmethod
    def check_args_2(args: Tuple[str, str], script_name: str = "study_data_set"):
        """Check_args_2."""
        if len(args) != 2:
            raise ApiError(
                code="missing_argument",
                message=f"The {script_name} script takes two arguments, key and value, in that order.",
            )

    def set_data_common(
        self, task_spec, study_id, user_id, workflow_id, script_name, file_id, *args
    ):
        """Set_data_common."""
        self.check_args_2(args, script_name=script_name)
        key = args[0]
        value = args[1]
        if value == "" or value is None:
            # We delete the data store if the value is empty
            return self.delete_data_store(study_id, user_id, file_id, *args)
        workflow_spec_id = None
        if workflow_id is not None:
            workflow = (
                session.query(WorkflowModel)
                .filter(WorkflowModel.id == workflow_id)
                .first()
            )
            workflow_spec_id = workflow.workflow_spec_id

        # Check if this data store is previously set
        query = session.query(DataStoreModel).filter(DataStoreModel.key == key)
        if study_id:
            query = query.filter(DataStoreModel.study_id == study_id)
        elif file_id:
            query = query.filter(DataStoreModel.file_id == file_id)
        elif user_id:
            query = query.filter(DataStoreModel.user_id == user_id)
        result = query.order_by(desc(DataStoreModel.last_updated)).all()
        if result:
            dsm = result[0]
            dsm.value = value
            if task_spec:
                dsm.task_spec = task_spec
            if workflow_id:
                dsm.workflow_id = workflow_id
            if workflow_spec_id:
                dsm.spec_id = workflow_spec_id
            if len(result) > 1:
                # We had a bug where we had created new records instead of updating values of existing records
                # This just gets rid of all the old unused records
                self.delete_extra_data_stores(result[1:])
        else:
            dsm = DataStoreModel(
                key=key,
                value=value,
                study_id=study_id,
                task_spec=task_spec,
                user_id=user_id,  # Make this available to any User
                file_id=file_id,
                workflow_id=workflow_id,
                spec_id=workflow_spec_id,
            )
        session.add(dsm)
        session.commit()

        return dsm.value

    def get_data_common(self, study_id: str, user_id: str, script_name: str, file_id: (str | None) = None, *args: Any) -> Any:
        """Get_data_common."""
        self.check_args(args, 2, script_name)
        record = (
            session.query(DataStoreModel)
            .filter_by(study_id=study_id, user_id=user_id, file_id=file_id, key=args[0])
            .first()
        )
        if record:
            return record.value
        else:
            # This is a possible default value passed in from the data_store get methods
            if len(args) == 2:
                return args[1]

    @staticmethod
    def get_multi_common(study_id: str, user_id: str, file_id: (str | None) = None) -> sqlalchemy.orm.Query:
        """Get_multi_common."""
        results = session.query(DataStoreModel).filter_by(
            study_id=study_id, user_id=user_id, file_id=file_id
        )
        return results

    @staticmethod
    def delete_data_store(study_id: str, user_id: str, file_id: str, *args: Any) -> None:
        """Delete_data_store."""
        query = session.query(DataStoreModel).filter(DataStoreModel.key == args[0])
        if user_id:
            query = query.filter(DataStoreModel.user_id == user_id)
        elif file_id:
            query = query.filter(DataStoreModel.file_id == file_id)
        elif study_id:
            query = query.filter(DataStoreModel.study_id == study_id)
        record = query.first()
        if record is not None:
            session.delete(record)
            session.commit()

    @staticmethod
    def delete_extra_data_stores(records: list[DataStoreModel]) -> None:
        """We had a bug where we created new records instead of updating existing records.

        We use this to clean up all the extra records.
        We may remove this method in the future.
        """
        for record in records:
            session.query(DataStoreModel).filter(
                DataStoreModel.id == record.id
            ).delete()
        session.commit()
