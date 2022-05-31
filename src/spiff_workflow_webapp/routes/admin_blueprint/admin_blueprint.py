"""APIs for dealing with process groups, process models, and process instances."""
from typing import Any

from flask import Blueprint, render_template
from flask_bpmn.models.db import db
from flask import request

from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.services.process_instance_processor import ProcessInstanceProcessor
from spiff_workflow_webapp.services.process_instance_service import ProcessInstanceService
from spiff_workflow_webapp.services.spec_file_service import SpecFileService
from spiff_workflow_webapp.services.process_model_service import ProcessModelService

admin_blueprint = Blueprint("admin", __name__, template_folder='templates', static_folder='static')


@admin_blueprint.route("/index", methods=["GET"])
def hello_world():
    """Hello_world."""
    return render_template('index.html')


@admin_blueprint.route("/view/<process_model_id>/<file_id>", methods=["GET"])
def view_bpmn(process_model_id, file_id):
    """View_bpmn."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)
    return render_template('view.html', bpmn_xml=bpmn_xml.decode("utf-8"))


@admin_blueprint.route("/run/<process_model_id>", methods=["GET"])
def run_bpmn(process_model_id):
    """Run_bpmn."""
    user = find_or_create_user('Mr. Test')  # Fixme - sheesh!
    process_instance = ProcessInstanceService.create_process_instance(process_model_id, user)
    processor = ProcessInstanceProcessor(process_instance)
    processor.do_engine_steps()
    result = processor.get_data()

    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)

    return render_template('view.html', bpmn_xml=bpmn_xml.decode("utf-8"), result=result,
                           process_model_id=process_model_id)


@admin_blueprint.route("/edit/<process_model_id>", methods=["GET"])
def edit_bpmn(process_model_id):
    """Edit_bpmn."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)

    return render_template('edit.html', bpmn_xml=bpmn_xml.decode("utf-8"),
                           process_model_id=process_model_id)


@admin_blueprint.route("/save/<process_model_id>", methods=["POST"])
def save_bpmn(process_model_id):
    """Save_bpmn."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model, process_model.primary_file_name)
    SpecFileService.update_file(process_model, process_model.primary_file_name, request.get_data())
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)
    return render_template('edit.html', bpmn_xml=bpmn_xml.decode("utf-8"),
                           process_model_id=process_model_id)


@admin_blueprint.route("/process-groups/<process_group_id>", methods=["GET"])
def process_group_show(process_group_id):
    """Show_process_group."""
    process_group = ProcessModelService().get_process_group(process_group_id)
    return render_template('process_group_show.html', process_group=process_group)


@admin_blueprint.route("/process-groups", methods=["GET"])
def list_process_groups():
    """List_process_groups."""
    process_groups = ProcessModelService().get_process_groups()
    return render_template('process_groups.html', process_groups=process_groups)


@admin_blueprint.route("/process-models/<process_model_id>", methods=["GET"])
def process_model_show(process_model_id):
    """Show_process_model."""
    process_model = ProcessModelService().get_spec(process_model_id)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)
    return render_template('process_model_show.html', process_model=process_model, bpmn_xml=bpmn_xml)


@admin_blueprint.route("/process-models", methods=["GET"])
def list_process_models():
    """List_process_models."""
    models = ProcessModelService().get_specs()
    return render_template('process_models.html', models=models)


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username)
        db.session.add(user)
        db.session.commit()
    return user
