"""Process_instance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import TypedDict

from flask_bpmn.models.db import db
from flask_bpmn.models.db import SpiffworkflowBaseDBModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService


ReportMetadata = dict[str, Any]


class ProcessInstanceReportResult(TypedDict):
    """ProcessInstanceReportResult."""

    report_metadata: ReportMetadata
    results: list[dict]


# https://stackoverflow.com/a/56842689/6090676
class Reversor:
    """Reversor."""

    def __init__(self, obj: Any):
        """__init__."""
        self.obj = obj

    def __eq__(self, other: Any) -> Any:
        """__eq__."""
        return other.obj == self.obj

    def __lt__(self, other: Any) -> Any:
        """__lt__."""
        return other.obj < self.obj


@dataclass
class ProcessInstanceReportModel(SpiffworkflowBaseDBModel):
    """ProcessInstanceReportModel."""

    __tablename__ = "process_instance_report"
    id = db.Column(db.Integer, primary_key=True)
    identifier: str = db.Column(db.String(50), nullable=False, index=True)
    process_model_identifier: str = db.Column(db.String(50), nullable=False, index=True)
    process_group_identifier = db.Column(db.String(50), nullable=False, index=True)
    report_metadata: dict = deferred(db.Column(db.JSON))  # type: ignore
    created_by_id = db.Column(ForeignKey(UserModel.id), nullable=False)
    created_by = relationship("UserModel")
    created_at_in_seconds = db.Column(db.Integer)
    updated_at_in_seconds = db.Column(db.Integer)

    # @property
    # def serialized(self) -> dict[str, Union[str, int]]:
    #     """Return object data in serializeable format."""
    #     return {
    #         "id": self.id,
    #         "process_model_identifier": self.process_model_identifier,
    #         "process_group_identifier": self.process_group_identifier,
    #         "report_metadata": self.report_metadata,
    #         "created_by": self.process_initiator_id,
    #         "created_at_in_seconds": self.created_at_in_seconds,
    #         "updated_at_in_seconds": self.updated_at_in_seconds,
    #     }

    @classmethod
    def add_fixtures(cls) -> None:
        """Add_fixtures."""
        try:
            process_model = ProcessModelService().get_process_model(
                group_id="sartography-admin", process_model_id="ticket"
            )
            json = {"order": "month asc"}
            user = UserModel.query.first()
            process_instance_report = cls(
                identifier="for-month",
                process_group_identifier=process_model.process_group_id,
                process_model_identifier=process_model.id,
                created_by_id=user.id,
                report_metadata=json,
            )
            db.session.add(process_instance_report)
            db.session.commit()

        except ProcessEntityNotFoundError:
            print("NOPE")
            print("NOPE")
            print("NOPE")
            print("NOPE")

    @classmethod
    def create_with_attributes(
        cls,
        identifier: str,
        process_group_identifier: str,
        process_model_identifier: str,
        report_metadata: dict,
        user: UserModel,
    ) -> ProcessInstanceReportModel:
        """Create_with_attributes."""
        process_model = ProcessModelService().get_process_model(
            group_id=process_group_identifier, process_model_id=process_model_identifier
        )
        process_instance_report = cls(
            identifier=identifier,
            process_group_identifier=process_model.process_group_id,
            process_model_identifier=process_model.id,
            created_by_id=user.id,
            report_metadata=report_metadata,
        )
        db.session.add(process_instance_report)
        db.session.commit()
        return process_instance_report

    def with_substitutions(self, field_value: Any, substitution_variables: dict) -> Any:
        """With_substitutions."""
        if substitution_variables is not None:
            for key, value in substitution_variables.items():
                if isinstance(value, str) or isinstance(value, int):
                    field_value = str(field_value).replace(
                        "{{" + key + "}}", str(value)
                    )
        return field_value

    # modeled after https://github.com/suyash248/sqlalchemy-json-querybuilder
    # just supports "equals" operator for now.
    # perhaps we will use the database instead of filtering in memory in the future and then we might use this lib directly.
    def passes_filter(
        self, process_instance_dict: dict, substitution_variables: dict
    ) -> bool:
        """Passes_filter."""
        process_instance_data = process_instance_dict["data"]
        if "filter_by" in self.report_metadata:
            for filter_by in self.report_metadata["filter_by"]:
                field_name = filter_by["field_name"]
                operator = filter_by["operator"]
                field_value = self.with_substitutions(
                    filter_by["field_value"], substitution_variables
                )
                if operator == "equals":
                    if str(process_instance_data.get(field_name)) != str(field_value):
                        return False

        return True

    def order_things(self, process_instance_dicts: list) -> list:
        """Order_things."""
        order_by = self.report_metadata["order_by"]

        def order_by_function_for_lambda(process_instance_dict: dict) -> list[Reversor]:
            """Order_by_function_for_lambda."""
            comparison_values = []
            for order_by_item in order_by:
                if order_by_item.startswith("-"):
                    # remove leading - from order_by_item
                    order_by_item = order_by_item[1:]
                    sort_value = process_instance_dict["data"].get(order_by_item)
                    comparison_values.append(Reversor(sort_value))
                else:
                    sort_value = process_instance_dict["data"].get(order_by_item)
                    comparison_values.append(sort_value)
            return comparison_values

        return sorted(process_instance_dicts, key=order_by_function_for_lambda)

    def generate_report(
        self,
        process_instances: list[ProcessInstanceModel],
        substitution_variables: dict | None,
    ) -> ProcessInstanceReportResult:
        """Generate_report."""
        if substitution_variables is None:
            substitution_variables = {}

        def to_serialized(process_instance: ProcessInstanceModel) -> dict:
            """To_serialized."""
            processor = ProcessInstanceProcessor(process_instance)
            process_instance.data = processor.get_data()
            return process_instance.serialized

        process_instance_dicts = map(to_serialized, process_instances)
        results = []
        for process_instance_dict in process_instance_dicts:
            if self.passes_filter(process_instance_dict, substitution_variables):
                results.append(process_instance_dict)

        if "order_by" in self.report_metadata:
            results = self.order_things(results)

        if "columns" in self.report_metadata:
            column_keys_to_keep = [
                c["accessor"] for c in self.report_metadata["columns"]
            ]

            pruned_results = []
            for result in results:
                data = result["data"]
                dict_you_want = {
                    your_key: data[your_key]
                    for your_key in column_keys_to_keep
                    if data.get(your_key)
                }
                pruned_results.append(dict_you_want)
            results = pruned_results

        return ProcessInstanceReportResult(
            report_metadata=self.report_metadata, results=results
        )
