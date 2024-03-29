"""Dev."""
from os import environ

SPIFFWORKFLOW_BACKEND_GIT_PUBLISH_TARGET_BRANCH = environ.get(
    "SPIFFWORKFLOW_BACKEND_GIT_PUBLISH_TARGET_BRANCH", default="staging"
)
SPIFFWORKFLOW_BACKEND_GIT_USERNAME = environ.get(
    "SPIFFWORKFLOW_BACKEND_GIT_USERNAME", default="sartography-automated-committer"
)
SPIFFWORKFLOW_BACKEND_GIT_USER_EMAIL = environ.get(
    "SPIFFWORKFLOW_BACKEND_GIT_USER_EMAIL",
    default="sartography-automated-committer@users.noreply.github.com",
)
SPIFFWORKFLOW_BACKEND_PERMISSIONS_FILE_NAME = "dev.yml"
