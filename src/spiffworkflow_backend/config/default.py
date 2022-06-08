"""Default."""
import re
from os import environ

BPMN_SPEC_ABSOLUTE_DIR = environ.get("BPMN_SPEC_ABSOLUTE_DIR", default="")
CORS_DEFAULT = "*"
CORS_ALLOW_ORIGINS = re.split(
    r",\s*", environ.get("CORS_ALLOW_ORIGINS", default=CORS_DEFAULT)
)
