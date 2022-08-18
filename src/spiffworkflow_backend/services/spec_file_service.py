"""Spec_file_service."""
import os
import shutil
from datetime import datetime
from typing import List
from typing import Optional

from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db
from lxml import etree  # type: ignore
from lxml.etree import _Element  # type: ignore
from lxml.etree import Element as EtreeElement
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException  # type: ignore

from spiffworkflow_backend.models.file import File
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.message_correlation_property import (
    MessageCorrelationPropertyModel,
)
from spiffworkflow_backend.models.message_model import MessageModel
from spiffworkflow_backend.models.message_triggerable_process_model import (
    MessageTriggerableProcessModel,
)
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.services.file_system_service import FileSystemService


class SpecFileService(FileSystemService):
    """SpecFileService."""

    """We store spec files on the file system. This allows us to take advantage of Git for
       syncing and versioning.
        The files are stored in a directory whose path is determined by the category and spec names.
    """

    @staticmethod
    def get_files(
        process_model_info: ProcessModelInfo,
        file_name: Optional[str] = None,
        include_libraries: bool = False,
        extension_filter: str = "",
    ) -> List[File]:
        """Return all files associated with a workflow specification."""
        path = SpecFileService.workflow_path(process_model_info)
        files = SpecFileService._get_files(path, file_name)
        if include_libraries:
            for lib_name in process_model_info.libraries:
                lib_path = SpecFileService.library_path(lib_name)
                files.extend(SpecFileService._get_files(lib_path, file_name))

        if extension_filter != "":
            files = list(
                filter(lambda file: file.name.endswith(extension_filter), files)
            )

        return files

    @staticmethod
    def add_file(
        process_model_info: ProcessModelInfo, file_name: str, binary_data: bytes
    ) -> File:
        """Add_file."""
        # Same as update
        return SpecFileService.update_file(process_model_info, file_name, binary_data)

    @staticmethod
    def update_file(
        process_model_info: ProcessModelInfo, file_name: str, binary_data: bytes
    ) -> File:
        """Update_file."""
        SpecFileService.assert_valid_file_name(file_name)
        file_path = SpecFileService.file_path(process_model_info, file_name)
        SpecFileService.write_file_data_to_system(file_path, binary_data)
        file = SpecFileService.to_file_object(file_name, file_path)
        if file_name == process_model_info.primary_file_name:
            SpecFileService.set_primary_bpmn(process_model_info, file_name, binary_data)
        elif process_model_info.primary_file_name is None and file.type == str(
            FileType.bpmn
        ):
            # If no primary process exists, make this pirmary process.
            SpecFileService.set_primary_bpmn(process_model_info, file_name, binary_data)

        return file

    @staticmethod
    def get_data(process_model_info: ProcessModelInfo, file_name: str) -> bytes:
        """Get_data."""
        file_path = SpecFileService.file_path(process_model_info, file_name)
        if not os.path.exists(file_path):
            # If the file isn't here, it may be in a library
            for lib in process_model_info.libraries:
                file_path = SpecFileService.library_path(lib)
                file_path = os.path.join(file_path, file_name)
                if os.path.exists(file_path):
                    break
        if not os.path.exists(file_path):
            raise ApiError(
                "unknown_file",
                f"No file found with name {file_name} in {process_model_info.display_name}",
            )
        with open(file_path, "rb") as f_handle:
            spec_file_data = f_handle.read()
        return spec_file_data

    @staticmethod
    def file_path(spec: ProcessModelInfo, file_name: str) -> str:
        """File_path."""
        return os.path.join(SpecFileService.workflow_path(spec), file_name)

    @staticmethod
    def last_modified(spec: ProcessModelInfo, file_name: str) -> datetime:
        """Last_modified."""
        path = SpecFileService.file_path(spec, file_name)
        return FileSystemService._last_modified(path)

    @staticmethod
    def timestamp(spec: ProcessModelInfo, file_name: str) -> float:
        """Timestamp."""
        path = SpecFileService.file_path(spec, file_name)
        return FileSystemService._timestamp(path)

    @staticmethod
    def delete_file(spec: ProcessModelInfo, file_name: str) -> None:
        """Delete_file."""
        # Fixme: Remember to remove the lookup files when the spec file is removed.
        # lookup_files = session.query(LookupFileModel).filter_by(file_model_id=file_id).all()
        # for lf in lookup_files:
        #     session.query(LookupDataModel).filter_by(lookup_file_model_id=lf.id).delete()
        #     session.query(LookupFileModel).filter_by(id=lf.id).delete()
        file_path = SpecFileService.file_path(spec, file_name)
        os.remove(file_path)

    @staticmethod
    def delete_all_files(spec: ProcessModelInfo) -> None:
        """Delete_all_files."""
        dir_path = SpecFileService.workflow_path(spec)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    @staticmethod
    def set_primary_bpmn(
        process_model_info: ProcessModelInfo,
        file_name: str,
        binary_data: Optional[bytes] = None,
    ) -> None:
        """Set_primary_bpmn."""
        # If this is a BPMN, extract the process id, and determine if it is contains swim lanes.
        extension = SpecFileService.get_extension(file_name)
        file_type = FileType[extension]
        if file_type == FileType.bpmn:
            if not binary_data:
                binary_data = SpecFileService.get_data(process_model_info, file_name)
            try:
                bpmn: EtreeElement = etree.fromstring(binary_data)
                process_model_info.primary_process_id = SpecFileService.get_process_id(
                    bpmn
                )
                process_model_info.primary_file_name = file_name
                process_model_info.is_review = SpecFileService.has_swimlane(bpmn)
                SpecFileService.check_for_message_models(bpmn, process_model_info)

            except etree.XMLSyntaxError as xse:
                raise ApiError(
                    "invalid_xml",
                    "Failed to parse xml: " + str(xse),
                    file_name=file_name,
                ) from xse
            except ValidationException as ve:
                if ve.args[0].find("No executable process tag found") >= 0:
                    raise ApiError(
                        code="missing_executable_option",
                        message="No executable process tag found. Please make sure the Executable option is set in the workflow.",
                    ) from ve
                else:
                    raise ApiError(
                        code="validation_error",
                        message=f"There was an error validating your workflow. Original message is: {ve}",
                    ) from ve
        else:
            raise ApiError(
                "invalid_xml",
                "Only a BPMN can be the primary file.",
                file_name=file_name,
            )

    @staticmethod
    def has_swimlane(et_root: _Element) -> bool:
        """Look through XML and determine if there are any lanes present that have a label."""
        elements = et_root.xpath(
            "//bpmn:lane",
            namespaces={"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"},
        )
        retval = False
        for el in elements:
            if el.get("name"):
                retval = True
        return retval

    @staticmethod
    def get_process_id(et_root: _Element) -> str:
        """Get_process_id."""
        process_elements = []
        for child in et_root:
            if child.tag.endswith("process") and child.attrib.get(
                "isExecutable", False
            ):
                process_elements.append(child)

        if len(process_elements) == 0:
            raise ValidationException("No executable process tag found")

        # There are multiple root elements
        if len(process_elements) > 1:

            # Look for the element that has the startEvent in it
            for e in process_elements:
                this_element: EtreeElement = e
                for child_element in list(this_element):
                    if child_element.tag.endswith("startEvent"):
                        # coorce Any to string
                        return str(this_element.attrib["id"])

            raise ValidationException(
                "No start event found in %s" % et_root.attrib["id"]
            )

        return str(process_elements[0].attrib["id"])

    @staticmethod
    def check_for_message_models(
        et_root: _Element, process_model_info: ProcessModelInfo
    ) -> None:
        """Check_for_message_models."""
        for child in et_root:
            if child.tag.endswith("message"):
                message_identifier = child.attrib.get("id")
                message_name = child.attrib.get("name")
                if message_identifier is None:
                    raise ValidationException(
                        "Message identifier is missing from bpmn xml"
                    )

                message_model = MessageModel.query.filter_by(
                    identifier=message_identifier
                ).first()
                if message_model is None:
                    message_model = MessageModel(
                        identifier=message_identifier, name=message_name
                    )
                    db.session.add(message_model)
                    db.session.commit()

        for child in et_root:
            if child.tag.endswith("}process"):
                message_event_definitions = child.xpath(
                    "//bpmn:startEvent/bpmn:messageEventDefinition",
                    namespaces={"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"},
                )
                if message_event_definitions:
                    message_event_definition = message_event_definitions[0]
                    message_model_identifier = message_event_definition.attrib.get(
                        "messageRef"
                    )
                    if message_model_identifier is None:
                        raise ValidationException(
                            "Could not find messageRef from message event definition: {message_event_definition}"
                        )

                    message_model = MessageModel.query.filter_by(
                        identifier=message_model_identifier
                    ).first()
                    if message_model is None:
                        raise ValidationException(
                            f"Could not find message model with identifier '{message_model_identifier}'"
                            f"specified by message event definition: {message_event_definition}"
                        )

                    message_triggerable_process_model = (
                        MessageTriggerableProcessModel.query.filter_by(
                            message_model_id=message_model.id,
                        ).first()
                    )

                    if message_triggerable_process_model is None:
                        message_triggerable_process_model = MessageTriggerableProcessModel(
                            message_model_id=message_model.id,
                            process_model_identifier=process_model_info.id,
                            process_group_identifier=process_model_info.process_group_id,
                        )
                        db.session.add(message_triggerable_process_model)
                        db.session.commit()
                    else:
                        if (
                            message_triggerable_process_model.process_model_identifier
                            != process_model_info.id
                            or message_triggerable_process_model.process_group_identifier
                            != process_model_info.process_group_id
                        ):
                            raise ValidationException(
                                f"Message model is already used to start process model '{process_model_info.process_group_id}/{process_model_info.id}'"
                            )

        for child in et_root:
            if child.tag.endswith("correlationProperty"):
                correlation_identifier = child.attrib.get("id")
                if correlation_identifier is None:
                    raise ValidationException(
                        "Correlation identifier is missing from bpmn xml"
                    )
                correlation_property_retrieval_expressions = child.xpath(
                    "//bpmn:correlationPropertyRetrievalExpression",
                    namespaces={"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"},
                )
                if not correlation_property_retrieval_expressions:
                    raise ValidationException(
                        "Correlation is missing correlation property retrieval expressions: {correlation_identifier}"
                    )

                for cpre in correlation_property_retrieval_expressions:
                    message_identifier = cpre.attrib.get("messageRef")
                    if message_identifier is None:
                        raise ValidationException(
                            f"Message identifier is missing from correlation property: {correlation_identifier}"
                        )
                    message_model = MessageModel.query.filter_by(
                        identifier=message_identifier
                    ).first()
                    if message_model is None:
                        raise ValidationException(
                            f"Could not find message model with identifier '{message_identifier}'"
                            f"specified by correlation: {correlation_identifier}"
                        )

                    message_correlation_property = (
                        MessageCorrelationPropertyModel.query.filter_by(
                            identifier=correlation_identifier,
                            message_model_id=message_model.id,
                        ).first()
                    )
                    if message_correlation_property is None:
                        message_correlation_property = MessageCorrelationPropertyModel(
                            identifier=correlation_identifier,
                            message_model_id=message_model.id,
                        )
                        db.session.add(message_correlation_property)
                        db.session.commit()
