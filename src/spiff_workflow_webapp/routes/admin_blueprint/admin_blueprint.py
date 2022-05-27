"""APIs for dealing with process groups, process models, and process instances."""
from typing import Any

import connexion
from flask import Blueprint, g, render_template
from flask_bpmn.models.db import db

from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.services.process_instance_processor import ProcessInstanceProcessor
from spiff_workflow_webapp.services.process_instance_service import ProcessInstanceService
from spiff_workflow_webapp.services.user_service import UserService
from spiff_workflow_webapp.services.spec_file_service import SpecFileService
from spiff_workflow_webapp.services.process_model_service import ProcessModelService

admin_blueprint = Blueprint("admin", __name__, template_folder='templates', static_folder='static')

@admin_blueprint.route("/index", methods=["GET"])
def hello_world():
    return render_template('index.html')


@admin_blueprint.route("/view/<process_model_id>/<file_id>", methods=["GET"])
def view_bpmn(process_model_id, file_id):
    process_model = ProcessModelService().get_spec(process_model_id)
    files = SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, files[0].name)
    return render_template('view.html', bpmn_xml=bpmn_xml.decode("utf-8") )

@admin_blueprint.route("/run/<process_model_id>/<file_id>", methods=["GET"])
def run_bpmn(process_model_id, file_id):
    user = find_or_create_user('Mr. Test') # Fixme - sheesh!
    process_instance = ProcessInstanceService.create_process_instance(process_model_id, user)
    processor = ProcessInstanceProcessor(process_instance)
    processor.do_engine_steps()
    result = processor.get_data()

    process_model = ProcessModelService().get_spec(process_model_id)
    files = SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, files[0].name)

    return render_template('view.html', bpmn_xml=bpmn_xml.decode("utf-8"), result=result)


def find_or_create_user(username: str = "test_user1") -> Any:
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username)
        db.session.add(user)
        db.session.commit()
    return user