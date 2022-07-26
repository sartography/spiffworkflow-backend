"""APIs for dealing with process groups, process models, and process instances."""
import json
import uuid
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import connexion  # type: ignore
import flask.wrappers
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import make_response
from flask import request
from flask.wrappers import Response
from flask_bpmn.api.api_error import ApiError
from flask_bpmn.models.db import db
from SpiffWorkflow import Task as SpiffTask  # type: ignore
from SpiffWorkflow import TaskState
from sqlalchemy import desc

from spiffworkflow_backend.exceptions.process_entity_not_found_error import (
    ProcessEntityNotFoundError,
)
from spiffworkflow_backend.models.active_task import ActiveTaskModel
from spiffworkflow_backend.models.file import FileSchema
from spiffworkflow_backend.models.file import FileType
from spiffworkflow_backend.models.principal import PrincipalModel
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceApiSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_instance import ProcessInstanceModelSchema
from spiffworkflow_backend.models.process_instance_report import (
    ProcessInstanceReportModel,
)
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.error_handling_service import ErrorHandlingService
from spiffworkflow_backend.services.process_instance_processor import (
    ProcessInstanceProcessor,
)
from spiffworkflow_backend.services.process_instance_service import (
    ProcessInstanceService,
)
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.spec_file_service import SpecFileService

# from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer  # type: ignore
# from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter  # type: ignore
# from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter  # type: ignore

process_api_blueprint = Blueprint("process_api", __name__)


def status() -> flask.wrappers.Response:
    """Status."""
    ProcessInstanceModel.query.filter().first()
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_group_add(
    body: Dict[str, Union[str, bool, int]]
) -> flask.wrappers.Response:
    """Add_process_group."""
    process_model_service = ProcessModelService()
    process_group = ProcessGroupSchema().load(body)
    process_model_service.add_process_group(process_group)
    return Response(
        json.dumps(ProcessGroupSchema().dump(process_group)),
        status=201,
        mimetype="application/json",
    )


def process_group_delete(process_group_id: str) -> flask.wrappers.Response:
    """Process_group_delete."""
    ProcessModelService().process_group_delete(process_group_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_group_update(
    process_group_id: str, body: Dict[str, Union[str, bool, int]]
) -> Dict[str, Union[str, bool, int]]:
    """Process Group Update."""
    process_group = ProcessGroupSchema().load(body)
    ProcessModelService().update_process_group(process_group)
    return ProcessGroupSchema().dump(process_group)  # type: ignore


def process_groups_list(page: int = 1, per_page: int = 100) -> flask.wrappers.Response:
    """Process_groups_list."""
    process_groups = sorted(ProcessModelService().get_process_groups())
    batch = ProcessModelService().get_batch(
        items=process_groups, page=page, per_page=per_page
    )
    pages = len(process_groups) // per_page
    remainder = len(process_groups) % per_page
    if remainder > 0:
        pages += 1
    response_json = {
        "results": ProcessGroupSchema(many=True).dump(batch),
        "pagination": {
            "count": len(batch),
            "total": len(process_groups),
            "pages": pages,
        },
    }
    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def process_group_show(
    process_group_id: str,
) -> Any:
    """Process_group_show."""
    try:
        process_group = ProcessModelService().get_process_group(process_group_id)
    except ProcessEntityNotFoundError as exception:
        raise (
            ApiError(
                code="process_group_cannot_be_found",
                message=f"Process group cannot be found: {process_group_id}",
                status_code=400,
            )
        ) from exception
    return ProcessGroupSchema().dump(process_group)


def process_model_add(
    body: Dict[str, Union[str, bool, int]]
) -> flask.wrappers.Response:
    """Add_process_model."""
    process_model_info = ProcessModelInfoSchema().load(body)
    if process_model_info is None:
        raise ApiError(
            code="process_model_could_not_be_created",
            message=f"Process Model could not be created from given body: {body}",
            status_code=400,
        )

    process_model_service = ProcessModelService()
    process_group = process_model_service.get_process_group(
        process_model_info.process_group_id
    )
    if process_group is None:
        raise ApiError(
            code="process_model_could_not_be_created",
            message=f"Process Model could not be created from given body because Process Group could not be found: {body}",
            status_code=400,
        )

    process_model_info.process_group = process_group
    workflows = process_model_service.cleanup_workflow_spec_display_order(process_group)
    size = len(workflows)
    process_model_info.display_order = size
    process_model_service.add_spec(process_model_info)
    return Response(
        json.dumps(ProcessModelInfoSchema().dump(process_model_info)),
        status=201,
        mimetype="application/json",
    )


def process_model_delete(
    process_group_id: str, process_model_id: str
) -> flask.wrappers.Response:
    """Process_model_delete."""
    ProcessModelService().process_model_delete(process_model_id)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_model_update(
    process_group_id: str, process_model_id: str, body: Dict[str, Union[str, bool, int]]
) -> Any:
    """Process_model_update."""
    process_model = ProcessModelInfoSchema().load(body)
    ProcessModelService().update_spec(process_model)
    return ProcessModelInfoSchema().dump(process_model)


def process_model_show(process_group_id: str, process_model_id: str) -> Any:
    """Process_model_show."""
    process_model = get_process_model(process_model_id, process_group_id)
    files = sorted(SpecFileService.get_files(process_model))
    process_model.files = files
    process_model_json = ProcessModelInfoSchema().dump(process_model)
    return process_model_json


def process_model_list(
    process_group_id: str, page: int = 1, per_page: int = 100
) -> flask.wrappers.Response:
    """Process model list!"""
    process_models = sorted(ProcessModelService().get_process_models(process_group_id))
    batch = ProcessModelService().get_batch(
        process_models, page=page, per_page=per_page
    )
    pages = len(process_models) // per_page
    remainder = len(process_models) % per_page
    if remainder > 0:
        pages += 1
    response_json = {
        "results": ProcessModelInfoSchema(many=True).dump(batch),
        "pagination": {
            "count": len(batch),
            "total": len(process_models),
            "pages": pages,
        },
    }

    return Response(json.dumps(response_json), status=200, mimetype="application/json")


def get_file(process_group_id: str, process_model_id: str, file_name: str) -> Any:
    """Get_file."""
    process_model = get_process_model(process_model_id, process_group_id)
    files = SpecFileService.get_files(process_model, file_name)
    if len(files) == 0:
        raise ApiError(
            code="unknown file",
            message=f"No information exists for file {file_name}"
            f" it does not exist in workflow {process_model_id}.",
            status_code=404,
        )

    file = files[0]
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    return FileSchema().dump(file)


def process_model_file_update(
    process_group_id: str, process_model_id: str, file_name: str
) -> flask.wrappers.Response:
    """Process_model_file_save."""
    process_model = get_process_model(process_model_id, process_group_id)

    request_file = get_file_from_request()
    request_file_contents = request_file.stream.read()
    if not request_file_contents:
        raise ApiError(
            code="file_contents_empty",
            message="Given request file does not have any content",
            status_code=400,
        )

    SpecFileService.update_file(process_model, file_name, request_file_contents)
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def add_file(process_group_id: str, process_model_id: str) -> flask.wrappers.Response:
    """Add_file."""
    process_model_service = ProcessModelService()
    process_model = get_process_model(process_model_id, process_group_id)
    request_file = get_file_from_request()
    if not request_file.filename:
        raise ApiError(
            code="could_not_get_filename",
            message="Could not get filename from request",
            status_code=400,
        )

    file = SpecFileService.add_file(
        process_model, request_file.filename, request_file.stream.read()
    )
    file_contents = SpecFileService.get_data(process_model, file.name)
    file.file_contents = file_contents
    file.process_model_id = process_model.id
    file.process_group_id = process_model.process_group_id
    if not process_model.primary_process_id and file.type == FileType.bpmn.value:
        SpecFileService.set_primary_bpmn(process_model, file.name)
        process_model_service.update_spec(process_model)
    return Response(
        json.dumps(FileSchema().dump(file)), status=201, mimetype="application/json"
    )


def process_instance_create(
    process_group_id: str, process_model_id: str
) -> flask.wrappers.Response:
    """Create_process_instance."""
    process_instance = ProcessInstanceService.create_process_instance(
        process_model_id, g.user, process_group_identifier=process_group_id
    )
    return Response(
        json.dumps(ProcessInstanceModelSchema().dump(process_instance)),
        status=201,
        mimetype="application/json",
    )


def process_instance_run(
    process_group_id: str,
    process_model_id: str,
    process_instance_id: int,
    do_engine_steps: bool = True,
) -> flask.wrappers.Response:
    """Process_instance_run."""
    process_instance = ProcessInstanceService().get_process_instance(
        process_instance_id
    )
    processor = ProcessInstanceProcessor(process_instance)

    if do_engine_steps:
        try:
            processor.do_engine_steps()
        except Exception as e:
            ErrorHandlingService().handle_error(processor, e)
            task = processor.bpmn_process_instance.last_task
            raise ApiError.from_task(
                code="unknown_exception",
                message=f"An unknown error occurred. Original error: {e}",
                status_code=400,
                task=task,
            ) from e
        processor.save()
        ProcessInstanceService.update_task_assignments(processor)

    process_instance_api = ProcessInstanceService.processor_to_process_instance_api(
        processor
    )
    process_instance_data = processor.get_data()
    process_instance_metadata = ProcessInstanceApiSchema().dump(process_instance_api)
    process_instance_metadata["data"] = process_instance_data
    return Response(
        json.dumps(process_instance_metadata), status=200, mimetype="application/json"
    )


def process_instance_list(
    process_group_id: str,
    process_model_id: str,
    page: int = 1,
    per_page: int = 100,
    start_from: Optional[int] = None,
    start_till: Optional[int] = None,
    end_from: Optional[int] = None,
    end_till: Optional[int] = None,
    process_status: Optional[str] = None,
) -> flask.wrappers.Response:
    """Process_instance_list."""
    process_model = get_process_model(process_model_id, process_group_id)

    results = ProcessInstanceModel.query.filter_by(
        process_model_identifier=process_model.id
    )

    # this can never happen. obviously the class has the columns it defines. this is just to appease mypy.
    if (
        ProcessInstanceModel.start_in_seconds is None
        or ProcessInstanceModel.end_in_seconds is None
    ):
        raise (
            ApiError(
                code="unexpected_condition",
                message="Something went very wrong",
                status_code=500,
            )
        )

    if start_from is not None:
        results = results.filter(ProcessInstanceModel.start_in_seconds >= start_from)
    if start_till is not None:
        results = results.filter(ProcessInstanceModel.start_in_seconds <= start_till)
    if end_from is not None:
        results = results.filter(ProcessInstanceModel.end_in_seconds >= end_from)
    if end_till is not None:
        results = results.filter(ProcessInstanceModel.end_in_seconds <= end_till)
    if process_status is not None:
        results = results.filter(ProcessInstanceModel.status == process_status)

    process_instances = results.order_by(
        ProcessInstanceModel.start_in_seconds.desc(), ProcessInstanceModel.id.desc()  # type: ignore
    ).paginate(page, per_page, False)

    response_json = {
        "results": process_instances.items,
        "pagination": {
            "count": len(process_instances.items),
            "total": process_instances.total,
            "pages": process_instances.pages,
        },
    }

    return make_response(jsonify(response_json), 200)


def process_instance_show(
    process_group_id: str, process_model_id: str, process_instance_id: int
) -> flask.wrappers.Response:
    """Create_process_instance."""
    process_instance = find_process_instance_by_id_or_raise(process_instance_id)
    process_model = get_process_model(process_model_id, process_group_id)

    if process_model.primary_file_name:
        bpmn_xml_file_contents = SpecFileService.get_data(
            process_model, process_model.primary_file_name
        )
        process_instance.bpmn_xml_file_contents = bpmn_xml_file_contents

    return make_response(jsonify(process_instance), 200)


def process_instance_delete(
    process_group_id: str, process_model_id: str, process_instance_id: int
) -> flask.wrappers.Response:
    """Create_process_instance."""
    process_instance = find_process_instance_by_id_or_raise(process_instance_id)

    db.session.delete(process_instance)
    db.session.commit()
    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_instance_report_list(
    process_group_id: str, process_model_id: str, page: int = 1, per_page: int = 100
) -> flask.wrappers.Response:
    """Process_instance_report_list."""
    process_model = get_process_model(process_model_id, process_group_id)

    process_instance_reports = ProcessInstanceReportModel.query.filter_by(
        process_group_identifier=process_group_id,
        process_model_identifier=process_model.id,
    ).all()

    return make_response(jsonify(process_instance_reports), 200)


def process_instance_report_create(
    process_group_id: str, process_model_id: str, body: Dict[str, Any]
) -> flask.wrappers.Response:
    """Process_instance_report_create."""
    ProcessInstanceReportModel.create_report(
        identifier=body["identifier"],
        process_group_identifier=process_group_id,
        process_model_identifier=process_model_id,
        user=g.user,
        report_metadata=body["report_metadata"],
    )

    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_instance_report_update(
    process_group_id: str,
    process_model_id: str,
    report_identifier: str,
    body: Dict[str, Any],
) -> flask.wrappers.Response:
    """Process_instance_report_create."""
    process_instance_report = ProcessInstanceReportModel.query.filter_by(
        identifier=report_identifier,
        process_group_identifier=process_group_id,
        process_model_identifier=process_model_id,
    ).first()
    if process_instance_report is None:
        raise ApiError(
            code="unknown_process_instance_report",
            message="Unknown process instance report",
            status_code=404,
        )

    process_instance_report.report_metadata = body["report_metadata"]
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_instance_report_delete(
    process_group_id: str,
    process_model_id: str,
    report_identifier: str,
) -> flask.wrappers.Response:
    """Process_instance_report_create."""
    process_instance_report = ProcessInstanceReportModel.query.filter_by(
        identifier=report_identifier,
        process_group_identifier=process_group_id,
        process_model_identifier=process_model_id,
    ).first()
    if process_instance_report is None:
        raise ApiError(
            code="unknown_process_instance_report",
            message="Unknown process instance report",
            status_code=404,
        )

    db.session.delete(process_instance_report)
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")


def process_instance_report_show(
    process_group_id: str,
    process_model_id: str,
    report_identifier: str,
    page: int = 1,
    per_page: int = 100,
) -> flask.wrappers.Response:
    """Process_instance_list."""
    process_model = get_process_model(process_model_id, process_group_id)

    process_instances = (
        ProcessInstanceModel.query.filter_by(process_model_identifier=process_model.id)
        .order_by(
            ProcessInstanceModel.start_in_seconds.desc(), ProcessInstanceModel.id.desc()  # type: ignore
        )
        .paginate(page, per_page, False)
    )

    process_instance_report = ProcessInstanceReportModel.query.filter_by(
        identifier=report_identifier
    ).first()
    if process_instance_report is None:
        raise ApiError(
            code="unknown_process_instance_report",
            message="Unknown process instance report",
            status_code=404,
        )

    substitution_variables = request.args.to_dict()
    result_dict = process_instance_report.generate_report(
        process_instances.items, substitution_variables
    )

    # update this if we go back to a database query instead of filtering in memory
    result_dict["pagination"] = {
        "count": len(result_dict["results"]),
        "total": len(result_dict["results"]),
        "pages": 1,
    }

    return Response(json.dumps(result_dict), status=200, mimetype="application/json")


def task_list_my_tasks(page: int = 1, per_page: int = 100) -> flask.wrappers.Response:
    """Task_list_my_tasks."""
    principal = find_principal_or_raise()

    active_tasks = (
        ActiveTaskModel.query.filter_by(assigned_principal_id=principal.id)
        .order_by(desc(ActiveTaskModel.id))  # type: ignore
        .paginate(page, per_page, False)
    )

    tasks = [active_task.to_task() for active_task in active_tasks.items]

    response_json = {
        "results": tasks,
        "pagination": {
            "count": len(active_tasks.items),
            "total": active_tasks.total,
            "pages": active_tasks.pages,
        },
    }

    return make_response(jsonify(response_json), 200)


def process_instance_task_list(
    process_instance_id: int, all_tasks: bool = False
) -> flask.wrappers.Response:
    """Process_instance_task_list."""
    process_instance = find_process_instance_by_id_or_raise(process_instance_id)
    processor = ProcessInstanceProcessor(process_instance)

    spiff_tasks = None
    if all_tasks:
        spiff_tasks = processor.bpmn_process_instance.get_tasks(TaskState.ANY_MASK)
    else:
        spiff_tasks = processor.get_all_user_tasks()

    tasks = []
    for spiff_task in spiff_tasks:
        task = ProcessInstanceService.spiff_task_to_api_task(spiff_task)
        task.data = spiff_task.data
        tasks.append(task)

    return make_response(jsonify(tasks), 200)


def task_show(process_instance_id: int, task_id: str) -> flask.wrappers.Response:
    """Task_list_my_tasks."""
    principal = find_principal_or_raise()

    process_instance = find_process_instance_by_id_or_raise(process_instance_id)
    process_model = get_process_model(
        process_instance.process_model_identifier,
        process_instance.process_group_identifier,
    )

    active_task_assigned_to_me = ActiveTaskModel.query.filter_by(
        process_instance_id=process_instance_id,
        task_id=task_id,
        assigned_principal_id=principal.id,
    ).first()

    form_schema_file_name = ""
    form_ui_schema_file_name = ""
    task = None
    if active_task_assigned_to_me:
        form_schema_file_name = active_task_assigned_to_me.form_file_name
        form_ui_schema_file_name = active_task_assigned_to_me.ui_form_file_name
        task = active_task_assigned_to_me.to_task()
    else:
        spiff_task = get_spiff_task_from_process_instance(task_id, process_instance)
        extensions = spiff_task.task_spec.extensions

        if "properties" in extensions:
            properties = extensions["properties"]
            if "formJsonSchemaFilename" in properties:
                form_schema_file_name = properties["formJsonSchemaFilename"]
            if "formUiSchemaFilename" in properties:
                form_ui_schema_file_name = properties["formUiSchemaFilename"]
        task = ProcessInstanceService.spiff_task_to_api_task(spiff_task)
        task.data = spiff_task.data

    if form_schema_file_name is None:
        raise (
            ApiError(
                code="missing_form_file",
                message=f"Cannot find a form file for process_instance_id: {process_instance_id}, task_id: {task_id}",
                status_code=500,
            )
        )

    form_contents = prepare_form_data(
        form_schema_file_name,
        task.data,
        process_model,
    )

    if form_contents:
        task.form_schema = form_contents

    if form_ui_schema_file_name:
        ui_form_contents = prepare_form_data(
            form_ui_schema_file_name,
            task.data,
            process_model,
        )
        if ui_form_contents:
            task.form_ui_schema = ui_form_contents

    return make_response(jsonify(task), 200)


def task_submit(
    process_instance_id: int,
    task_id: str,
    body: Dict[str, Any],
    terminate_loop: bool = False,
) -> flask.wrappers.Response:
    """Task_submit_user_data."""
    principal = find_principal_or_raise()
    active_task_assigned_to_me = find_active_task_by_id_or_raise(
        process_instance_id, task_id, principal.id
    )

    process_instance = find_process_instance_by_id_or_raise(
        active_task_assigned_to_me.process_instance_id
    )

    processor = ProcessInstanceProcessor(process_instance)
    spiff_task = get_spiff_task_from_process_instance(
        task_id, process_instance, processor=processor
    )

    if spiff_task.state != TaskState.READY:
        raise (
            ApiError(
                code="invalid_state",
                message="You may not update a task unless it is in the READY state.",
                status_code=400,
            )
        )

    if terminate_loop and spiff_task.is_looping():
        spiff_task.terminate_loop()

    # TODO: support repeating fields
    # Extract the details specific to the form submitted
    # form_data = WorkflowService().extract_form_data(body, spiff_task)

    ProcessInstanceService.complete_form_task(processor, spiff_task, body, g.user)

    # If we need to update all tasks, then get the next ready task and if it a multi-instance with the same
    # task spec, complete that form as well.
    # if update_all:
    #     last_index = spiff_task.task_info()["mi_index"]
    #     next_task = processor.next_task()
    #     while next_task and next_task.task_info()["mi_index"] > last_index:
    #         __update_task(processor, next_task, form_data, user)
    #         last_index = next_task.task_info()["mi_index"]
    #         next_task = processor.next_task()

    ProcessInstanceService.update_task_assignments(processor)

    next_active_task_assigned_to_me = ActiveTaskModel.query.filter_by(
        assigned_principal_id=principal.id, process_instance_id=process_instance.id
    ).first()
    if next_active_task_assigned_to_me:
        return make_response(jsonify(next_active_task_assigned_to_me.to_task()), 200)

    return Response(json.dumps({"ok": True}), status=202, mimetype="application/json")


def get_file_from_request() -> Any:
    """Get_file_from_request."""
    request_file = connexion.request.files.get("file")
    if not request_file:
        raise ApiError(
            code="no_file_given",
            message="Given request does not contain a file",
            status_code=400,
        )
    return request_file


def get_process_model(process_model_id: str, process_group_id: str) -> ProcessModelInfo:
    """Get_process_model."""
    process_model = None
    try:
        process_model = ProcessModelService().get_process_model(
            process_model_id, group_id=process_group_id
        )
    except ProcessEntityNotFoundError as exception:
        raise (
            ApiError(
                code="process_model_cannot_be_found",
                message=f"Process model cannot be found: {process_model_id}",
                status_code=400,
            )
        ) from exception

    return process_model


def find_principal_or_raise() -> PrincipalModel:
    """Find_principal_or_raise."""
    principal = PrincipalModel.query.filter_by(user_id=g.user.id).first()
    if principal is None:
        raise (
            ApiError(
                code="principal_not_found",
                message=f"Principal not found from user id: {g.user.id}",
                status_code=400,
            )
        )
    return principal  # type: ignore


def find_active_task_by_id_or_raise(
    process_instance_id: int, task_id: str, principal_id: PrincipalModel
) -> ActiveTaskModel:
    """Find_active_task_by_id_or_raise."""
    active_task_assigned_to_me = ActiveTaskModel.query.filter_by(
        process_instance_id=process_instance_id,
        task_id=task_id,
        assigned_principal_id=principal_id,
    ).first()
    if active_task_assigned_to_me is None:
        message = (
            f"Task not found for principal user {principal_id} "
            f"process_instance_id: {process_instance_id}, task_id: {task_id}"
        )
        raise (
            ApiError(
                code="task_not_found",
                message=message,
                status_code=400,
            )
        )
    return active_task_assigned_to_me  # type: ignore


def find_process_instance_by_id_or_raise(
    process_instance_id: int,
) -> ProcessInstanceModel:
    """Find_process_instance_by_id_or_raise."""
    process_instance = ProcessInstanceModel.query.filter_by(
        id=process_instance_id
    ).first()
    if process_instance is None:
        raise (
            ApiError(
                code="process_instance_cannot_be_found",
                message=f"Process instance cannot be found: {process_instance_id}",
                status_code=400,
            )
        )
    return process_instance  # type: ignore


def get_value_from_array_with_index(array: list, index: int) -> Any:
    """Get_value_from_array_with_index."""
    if index < 0:
        return None

    if index >= len(array):
        return None

    return array[index]


def prepare_form_data(
    form_file: str, task_data: Union[dict, None], process_model: ProcessModelInfo
) -> str:
    """Prepare_form_data."""
    if task_data is None:
        return ""

    file_contents = SpecFileService.get_data(process_model, form_file).decode("utf-8")

    # trade out pieces like "{{variable_name}}" for the corresponding form data value
    for key, value in task_data.items():
        if isinstance(value, str) or isinstance(value, int):
            file_contents = file_contents.replace("{{" + key + "}}", str(value))

    return file_contents


def get_spiff_task_from_process_instance(
    task_id: str,
    process_instance: ProcessInstanceModel,
    processor: Union[ProcessInstanceProcessor, None] = None,
) -> SpiffTask:
    """Get_spiff_task_from_process_instance."""
    if processor is None:
        processor = ProcessInstanceProcessor(process_instance)
    task_uuid = uuid.UUID(task_id)
    spiff_task = processor.bpmn_process_instance.get_task(task_uuid)

    if spiff_task is None:
        raise (
            ApiError(
                code="empty_task",
                message="Processor failed to obtain task.",
                status_code=500,
            )
        )
    return spiff_task
