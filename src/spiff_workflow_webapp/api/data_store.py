"""Methods to talk to the database."""
import json
from datetime import datetime
from typing import Any

from crc.models.data_store import DataStoreModel
from crc.models.data_store import DataStoreSchema
from crc.services.data_store_service import DataStoreBase
from flask import Blueprint
from sqlalchemy.orm import Session  # type: ignore

from spiff_workflow_webapp.api.api_error import ApiError

# from crc import session


def construct_blueprint(database_session: Session) -> Blueprint:
    """Construct_blueprint."""
    data_store_blueprint = Blueprint("data_store", __name__)
    database_session = database_session

    def study_multi_get(study_id: str) -> Any:
        """Get all data_store values for a given study_id study."""
        if study_id is None:
            raise ApiError("unknown_study", "Please provide a valid Study ID.")

        dsb = DataStoreBase()
        retval = dsb.get_multi_common(study_id, None)
        results = DataStoreSchema(many=True).dump(retval)
        return results

    def user_multi_get(user_id: str) -> Any:
        """Get all data values in the data_store for a userid."""
        if user_id is None:
            raise ApiError("unknown_study", "Please provide a valid UserID.")

        dsb = DataStoreBase()
        retval = dsb.get_multi_common(None, user_id)
        results = DataStoreSchema(many=True).dump(retval)
        return results

    def file_multi_get(file_id: str) -> Any:
        """Get all data values in the data store for a file_id."""
        if file_id is None:
            raise ApiError(
                code="unknown_file", message="Please provide a valid file id."
            )
        dsb = DataStoreBase()
        retval = dsb.get_multi_common(None, None, file_id=file_id)
        results = DataStoreSchema(many=True).dump(retval)
        return results

    def datastore_del(id: str) -> Any:
        """Delete a data store item for a key."""
        database_session.query(DataStoreModel).filter_by(id=id).delete()
        database_session.commit()
        json_value = json.dumps("deleted", ensure_ascii=False, indent=2)
        return json_value

    def datastore_get(id: str) -> Any:
        """Retrieve a data store item by a key."""
        item = database_session.query(DataStoreModel).filter_by(id=id).first()
        results = DataStoreSchema(many=False).dump(item)
        return results

    def update_datastore(id: str, body: dict) -> Any:
        """Allow a modification to a datastore item."""
        if id is None:
            raise ApiError("unknown_id", "Please provide a valid ID.")

        item = database_session.query(DataStoreModel).filter_by(id=id).first()
        if item is None:
            raise ApiError("unknown_item", 'The item "' + id + '" is not recognized.')

        DataStoreSchema().load(body, instance=item, database_session=database_session)
        item.last_updated = datetime.utcnow()
        database_session.add(item)
        database_session.commit()
        return DataStoreSchema().dump(item)

    def add_datastore(body: dict) -> Any:
        """Add a new datastore item."""
        if body.get(id, None):
            raise ApiError(
                "id_specified", "You may not specify an id for a new datastore item"
            )

        if "key" not in body:
            raise ApiError(
                "no_key", "You need to specify a key to add a datastore item"
            )

        if "value" not in body:
            raise ApiError(
                "no_value", "You need to specify a value to add a datastore item"
            )

        if (
            ("user_id" not in body)
            and ("study_id" not in body)
            and ("file_id" not in body)
        ):
            raise ApiError(
                "conflicting_values",
                "A datastore item should have either a study_id, user_id or file_id ",
            )

        present = 0
        for field in ["user_id", "study_id", "file_id"]:
            if field in body:
                present = present + 1
        if present > 1:
            message = "A datastore item should have one of a study_id, user_id or a file_id but not more than one of these"
            raise ApiError("conflicting_values", message)

        item = DataStoreSchema().load(body)
        # item.last_updated = datetime.utcnow()  # Do this in the database
        database_session.add(item)
        database_session.commit()
        return DataStoreSchema().dump(item)

    return data_store_blueprint
