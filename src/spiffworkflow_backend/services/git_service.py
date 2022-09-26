import os
from flask import current_app

from spiffworkflow_backend.models.process_model import ProcessModelInfo
from spiffworkflow_backend.services.file_system_service import FileSystemService


class GitService:

    @staticmethod
    def get_current_revision() -> str:
        bpmn_spec_absolute_dir = current_app.config["BPMN_SPEC_ABSOLUTE_DIR"]
        # The value includes a carriage return character at the end, so we don't grab the last character
        current_git_revision = os.popen(f"cd {bpmn_spec_absolute_dir} && git rev-parse --short HEAD").read()[:-1]
        return current_git_revision

    @staticmethod
    def get_instance_file_contents_for_revision(process_model: ProcessModelInfo, revision: str) -> str:
        bpmn_spec_absolute_dir = current_app.config["BPMN_SPEC_ABSOLUTE_DIR"]
        process_model_relative_path = FileSystemService.process_model_relative_path(process_model)
        shell_command = f"cd {bpmn_spec_absolute_dir} && git show {revision}:{process_model_relative_path}/{process_model.primary_file_name}"
        # git show 78ae5eb:category_number_one/script-task/script-task.bpmn
        file_contents = os.popen(shell_command).read()[:-1]
        return file_contents
