"""Example_data."""
import glob
import os

from flask import current_app

from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.spec_file_service import SpecFileService


class ExampleDataLoader:
    """ExampleDataLoader."""

    def create_spec(
        self,
        id: str,
        display_name: str = "",
        description: str = "",
        master_spec: bool = False,
        process_group_id: str = "",
        display_order: int = 0,
        from_tests: bool = False,
        standalone: bool = False,
        library: bool = False,
    ) -> ProcessModelInfo:
        """Assumes that a directory exists in static/bpmn with the same name as the given id.

        further assumes that the [id].bpmn is the primary file for the process model.
        returns an array of data models to be added to the database.
        """
        spec = ProcessModelInfo(
            id=id,
            display_name=display_name,
            description=description,
            process_group_id=process_group_id,
            display_order=display_order,
            is_master_spec=master_spec,
            standalone=standalone,
            library=library,
            primary_file_name="",
            primary_process_id="",
            is_review=False,
            libraries=[],
        )
        workflow_spec_service = ProcessModelService()
        workflow_spec_service.add_spec(spec)

        file_glob = ""
        if from_tests:
            file_glob = os.path.join(
                current_app.instance_path, "..", "..", "tests", "data", id, "*.*"
            )
        else:
            file_glob = os.path.join(current_app.root_path, "static", "bpmn", id, "*.*")

        files = glob.glob(file_glob)
        for file_path in files:
            if os.path.isdir(file_path):
                continue  # Don't try to process sub directories

            filename = os.path.basename(file_path)
            is_primary = filename.lower() == id + ".bpmn"
            file = None
            try:
                file = open(file_path, "rb")
                data = file.read()
                SpecFileService.add_file(
                    workflow_spec=spec, file_name=filename, binary_data=data
                )
                if is_primary:
                    SpecFileService.set_primary_bpmn(spec, filename, data)
                    workflow_spec_service = ProcessModelService()
                    workflow_spec_service.update_spec(spec)
            except IsADirectoryError:
                # Ignore sub directories
                pass
            finally:
                if file:
                    file.close()
        return spec
