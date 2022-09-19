"""Grabs tickets from csv and makes process instances."""
import os

from spiffworkflow_backend import create_app
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.spec_file_service import SpecFileService


def main():
    """Main."""
    os.environ["FLASK_ENV"] = "development"
    flask_env_key = "FLASK_SESSION_SECRET_KEY"
    os.environ[flask_env_key] = "whatevs"
    home = os.environ["HOME"]
    os.environ[
        "BPMN_SPEC_ABSOLUTE_DIR"
    ] = f"{home}/projects/github/sartography/sample-process-models"
    app = create_app()
    with app.app_context():
        no_primary = []
        process_models = ProcessModelService().get_process_models()
        for process_model in process_models:
            if process_model.primary_file_name:
                files = SpecFileService.get_files(
                    process_model, extension_filter="bpmn"
                )
                if len(files) == 1:
                    # print(f"primary_file_name: {process_model.primary_file_name}")
                    bpmn_xml_file_contents = SpecFileService.get_data(
                        process_model, process_model.primary_file_name
                    )
                    # bpmn_etree_element: EtreeElement = (
                    #     SpecFileService.get_etree_element_from_binary_data(
                    #         bpmn_xml_file_contents, process_model.primary_file_name
                    #     )
                    # )
                    # try:
                    #     attributes_to_update = {
                    #         "primary_process_id": (
                    #             SpecFileService.get_bpmn_process_identifier(
                    #                 bpmn_etree_element
                    #             )
                    #         ),
                    #     }
                    #     ProcessModelService().update_spec(
                    #         process_model, attributes_to_update
                    #     )
                    SpecFileService.update_file(
                        process_model,
                        process_model.primary_file_name,
                        bpmn_xml_file_contents,
                    )
                    # except Exception:
                    #     print(process_model.id)
            else:
                no_primary.append(process_model)
        for bpmn in no_primary:
            print(bpmn)


if __name__ == "__main__":
    main()
