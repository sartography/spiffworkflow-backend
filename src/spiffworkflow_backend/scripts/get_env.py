import requests
from flask import current_app

from spiffworkflow_backend.scripts.script import Script
from SpiffWorkflow import Task as SpiffTask  # type: ignore

class GetEnv(Script):

    def get_description(self):
        return """Returns the current environment - ie TESTING, STAGING, PRODUCTION"""

    def run(self, task: SpiffTask, environment_identifier: str, **kwargs):
        return environment_identifier
