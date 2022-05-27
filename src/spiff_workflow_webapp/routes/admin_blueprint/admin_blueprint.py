"""APIs for dealing with process groups, process models, and process instances."""

import connexion
from flask import Blueprint, g, render_template

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
