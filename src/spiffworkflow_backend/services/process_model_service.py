"""Process_model_service."""
import json
import os
import shutil
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.process_group import ProcessGroup
from spiffworkflow_backend.models.process_group import ProcessGroupSchema
from spiffworkflow_backend.models.process_instance import ProcessInstanceModel
from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.models.process_model import ProcessModelInfoSchema
from spiffworkflow_backend.services.file_system_service import FileSystemService


class ProcessModelService(FileSystemService):
    """ProcessModelService."""

    """This is a way of persisting json files to the file system in a way that mimics the data
    as it would have been stored in the database. This is specific to Workflow Specifications, and
    Workflow Specification process_groups.
    We do this, so we can easily drop in a new configuration on the file system, and change all
    the workflow process_models at once, or manage those file in a git repository. """

    GROUP_SCHEMA = ProcessGroupSchema()
    WF_SCHEMA = ProcessModelInfoSchema()

    @staticmethod
    def get_batch(
        items: List[Union[Any, ProcessGroup, ProcessModelInfo]],
        page: int = 1,
        per_page: int = 10,
    ) -> List[Union[Any, ProcessGroup, ProcessModelInfo]]:
        """Get_batch."""
        start = (page - 1) * per_page
        end = start + per_page
        return items[start:end]

    def add_spec(self, spec: ProcessModelInfo) -> None:
        """Add_spec."""
        display_order = self.next_display_order(spec)
        spec.display_order = display_order
        self.update_spec(spec)

    def update_spec(self, spec: ProcessModelInfo) -> None:
        """Update_spec."""
        spec_path = self.workflow_path(spec)
        if spec.is_master_spec or spec.library or spec.standalone:
            spec.process_group_id = ""
        os.makedirs(spec_path, exist_ok=True)
        json_path = os.path.join(spec_path, self.WF_JSON_FILE)
        with open(json_path, "w") as wf_json:
            json.dump(self.WF_SCHEMA.dump(spec), wf_json, indent=4)

    def process_model_delete(self, process_model_id: str) -> None:
        """Delete Procecss Model."""
        instances = ProcessInstanceModel.query.filter(
            ProcessInstanceModel.process_model_identifier == process_model_id
        ).all()
        if len(instances) > 0:
            raise ApiError(
                code="existing_instances",
                message=f"We cannot delete the model `{process_model_id}`, there are existing instances that depend on it.",
            )
        process_model = self.get_process_model(process_model_id)
        if not process_model:
            return
        if process_model.library:
            self.__remove_library_references(process_model.id)
        path = self.workflow_path(process_model)
        shutil.rmtree(path)

    def __remove_library_references(self, spec_id):
        """__remove_library_references."""
        for process_model in self.get_process_models():
            if spec_id in process_model.libraries:
                process_model.libraries.remove(spec_id)
                self.update_spec(process_model)

    @property
    def master_spec(self):
        """Master_spec."""
        return self.get_master_spec()

    def get_master_spec(self) -> None:
        """Get_master_spec."""
        path = os.path.join(
            FileSystemService.root_path(), FileSystemService.MASTER_SPECIFICATION
        )
        if os.path.exists(path):
            return self.__scan_spec(path, FileSystemService.MASTER_SPECIFICATION)

    def get_process_model(
        self, process_model_id: str, group_id: Optional[str] = None
    ) -> Optional[ProcessModelInfo]:
        """Get a process model from a model and group id."""
        if not os.path.exists(FileSystemService.root_path()):
            return  # Nothing to scan yet.  There are no files.

        master_spec = self.get_master_spec()
        if master_spec and master_spec.id == process_model_id:
            return master_spec
        if group_id is not None:
            for process_model in self.get_process_group(group_id).process_models:
                if process_model_id == process_model.id:
                    return process_model
        with os.scandir(FileSystemService.root_path()) as process_group_dirs:
            for item in process_group_dirs:
                process_group_dir = item
                if item.is_dir():
                    with os.scandir(item.path) as spec_dirs:
                        for sd in spec_dirs:
                            if sd.name == process_model_id:
                                # Now we have the process_group direcotry, and spec directory
                                process_group = self.__scan_process_group(
                                    process_group_dir
                                )
                                return self.__scan_spec(sd.path, sd.name, process_group)

    def get_process_models(
        self, process_group_id: Optional[str] = None
    ) -> List[ProcessModelInfo]:
        """Get process models."""
        if process_group_id is None:
            process_groups = self.get_process_groups()
        else:
            process_group = self.get_process_group(process_group_id)
            process_groups = [
                process_group,
            ]
        process_models = []
        for process_group in process_groups:
            process_models.extend(process_group.process_models)
        return process_models

    def reorder_spec(self, spec: ProcessModelInfo, direction):
        """Reorder_spec."""
        process_models = spec.process_group.process_models
        process_models.sort(key=lambda w: w.display_order)
        index = process_models.index(spec)
        if direction == "up" and index > 0:
            process_models[index - 1], process_models[index] = (
                process_models[index],
                process_models[index - 1],
            )
        if direction == "down" and index < len(process_models) - 1:
            process_models[index + 1], process_models[index] = (
                process_models[index],
                process_models[index + 1],
            )
        return self.cleanup_workflow_spec_display_order(spec.process_group)

    def cleanup_workflow_spec_display_order(
        self, process_group: ProcessGroup
    ) -> List[Union[Any, ProcessModelInfo]]:
        """Cleanup_workflow_spec_display_order."""
        index = 0
        if not process_group:
            return []
        for workflow in process_group.process_models:
            workflow.display_order = index
            self.update_spec(workflow)
            index += 1
        return process_group.process_models

    def get_process_groups(self) -> List[ProcessGroup]:
        """Returns the process_groups as a list in display order."""
        cat_list = self.__scan_process_groups()
        cat_list.sort(key=lambda w: w.display_order)
        return cat_list

    def get_libraries(self) -> List[ProcessModelInfo]:
        """Get_libraries."""
        process_group = self.get_process_group(self.LIBRARY_SPECS)
        if not process_group:
            return []
        return process_group.process_models

    def get_standalones(self) -> List[ProcessModelInfo]:
        """Get_standalones."""
        process_group = self.get_process_group(self.STAND_ALONE_SPECS)
        if not process_group:
            return []
        return process_group.process_models

    def get_process_group(self, process_group_id: str) -> Optional[ProcessGroup]:
        """Look for a given process_group, and return it."""
        if not os.path.exists(FileSystemService.root_path()):
            return  # Nothing to scan yet.  There are no files.
        with os.scandir(FileSystemService.root_path()) as directory_items:
            for item in directory_items:
                if item.is_dir() and item.name == process_group_id:
                    return self.__scan_process_group(item)

    def add_process_group(self, process_group: ProcessGroup) -> ProcessGroup:
        """Add_process_group."""
        display_order = len(self.get_process_groups())
        process_group.display_order = display_order
        return self.update_process_group(process_group)

    def update_process_group(self, process_group: ProcessGroup) -> ProcessGroup:
        """Update_process_group."""
        cat_path = self.process_group_path(process_group.id)
        os.makedirs(cat_path, exist_ok=True)
        json_path = os.path.join(cat_path, self.CAT_JSON_FILE)
        with open(json_path, "w") as cat_json:
            json.dump(self.GROUP_SCHEMA.dump(process_group), cat_json, indent=4)
        return process_group

    def process_group_delete(self, process_group_id: str) -> None:
        """Delete_process_group."""
        path = self.process_group_path(process_group_id)
        if os.path.exists(path):
            shutil.rmtree(path)
        self.cleanup_process_group_display_order()

    def reorder_workflow_spec_process_group(
        self, process_group: ProcessGroup, direction
    ):
        """Reorder_workflow_spec_process_group."""
        process_groups = self.get_process_groups()  # Returns an ordered list
        index = process_groups.index(process_group)
        if direction == "up" and index > 0:
            process_groups[index - 1], process_groups[index] = (
                process_groups[index],
                process_groups[index - 1],
            )
        if direction == "down" and index < len(process_groups) - 1:
            process_groups[index + 1], process_groups[index] = (
                process_groups[index],
                process_groups[index + 1],
            )
        index = 0
        for process_group in process_groups:
            process_group.display_order = index
            self.update_process_group(process_group)
            index += 1
        return process_groups

    def cleanup_process_group_display_order(self) -> List[Any]:
        """Cleanup_process_group_display_order."""
        process_groups = self.get_process_groups()  # Returns an ordered list
        index = 0
        for process_group in process_groups:
            process_group.display_order = index
            self.update_process_group(process_group)
            index += 1
        return process_groups

    def __scan_process_groups(self):
        """__scan_process_groups."""
        if not os.path.exists(FileSystemService.root_path()):
            return []  # Nothing to scan yet.  There are no files.

        with os.scandir(FileSystemService.root_path()) as directory_items:
            process_groups = []
            for item in directory_items:
                if item.is_dir() and not item.name[0] == ".":
                    if item.name == self.REFERENCE_FILES:
                        continue
                    elif item.name == self.MASTER_SPECIFICATION:
                        continue
                    elif item.name == self.LIBRARY_SPECS:
                        continue
                    elif item.name == self.STAND_ALONE_SPECS:
                        continue
                    process_groups.append(self.__scan_process_group(item))
            return process_groups

    def __scan_process_group(self, dir_item: os.DirEntry):
        """Reads the process_group.json file, and any workflow directories."""
        cat_path = os.path.join(dir_item.path, self.CAT_JSON_FILE)
        if os.path.exists(cat_path):
            with open(cat_path) as cat_json:
                data = json.load(cat_json)
                process_group = self.GROUP_SCHEMA.load(data)
        else:
            process_group = ProcessGroup(
                id=dir_item.name,
                display_name=dir_item.name,
                display_order=10000,
                admin=False,
            )
            with open(cat_path, "w") as wf_json:
                json.dump(self.GROUP_SCHEMA.dump(process_group), wf_json, indent=4)
        with os.scandir(dir_item.path) as workflow_dirs:
            process_group.process_models = []
            for item in workflow_dirs:
                if item.is_dir():
                    process_group.process_models.append(
                        self.__scan_spec(
                            item.path, item.name, process_group=process_group
                        )
                    )
            process_group.process_models.sort(key=lambda w: w.display_order)
        return process_group

    @staticmethod
    def _get_workflow_metas(study_id):
        """_get_workflow_metas."""
        # Add in the Workflows for each process_group
        # Fixme: moved fro the Study Service
        workflow_metas = []
        #        for workflow in workflow_models:
        #            workflow_metas.append(WorkflowMetadata.from_workflow(workflow))
        return workflow_metas

    def __scan_spec(self, path, name, process_group=None):
        """__scan_spec."""
        spec_path = os.path.join(path, self.WF_JSON_FILE)
        is_master = FileSystemService.MASTER_SPECIFICATION in spec_path

        if os.path.exists(spec_path):
            with open(spec_path) as wf_json:
                data = json.load(wf_json)
                spec = self.WF_SCHEMA.load(data)
        else:
            spec = ProcessModelInfo(
                id=name,
                library=False,
                standalone=False,
                is_master_spec=is_master,
                display_name=name,
                description="",
                primary_process_id="",
                primary_file_name="",
                display_order=0,
                is_review=False,
                libraries=[],
            )
            with open(spec_path, "w") as wf_json:
                json.dump(self.WF_SCHEMA.dump(spec), wf_json, indent=4)
        if process_group:
            spec.process_group = process_group
            spec.process_group_id = process_group.id
        return spec
