"""Default."""
import re
from os import environ

# Does the site allow self-registration of users
SELF_REGISTRATION = environ.get("SELF_REGISTRATION", default=False)

DEVELOPMENT = False

BPMN_SPEC_ABSOLUTE_DIR = environ.get("BPMN_SPEC_ABSOLUTE_DIR", default="")
CORS_DEFAULT = "*"
CORS_ALLOW_ORIGINS = re.split(
    r",\s*", environ.get("CORS_ALLOW_ORIGINS", default=CORS_DEFAULT)
)

# Keycloak server
KEYCLOAK_SERVER_URL = environ.get("KEYCLOAK_SERVER_URL", default="http://localhost:7002")
KEYCLOAK_CLIENT_ID = environ.get("KEYCLOAK_CLIENT_ID", default="spiffworkflow_backend")
KEYCLOAK_REALM_NAME = environ.get("KEYCLOAK_REALM_NAME", default="spiffworkflow")
KEYCLOAK_CLIENT_SECRET_KEY = environ.get("KEYCLOAK_CLIENT_SECRET_KEY", default="seciKpRanUReL0ksZaFm5nfjhMUKHVAO")  # noqa: S105
