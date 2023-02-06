"""Get current user."""
from typing import Any

from flask import current_app
from flask import g

from spiffworkflow_backend.models.script_attributes_context import (
    ScriptAttributesContext,
)
from spiffworkflow_backend.scripts.script import Script


class GetCurrentUser(Script):
    @staticmethod
    def requires_privileged_permissions() -> bool:
        """We have deemed this function safe to run without elevated permissions."""
        return False

    def get_description(self) -> str:
        """Get_description."""
        return """Return the current user."""

    def run(
        self,
        script_attributes_context: ScriptAttributesContext,
        *_args: Any,
        **kwargs: Any
    ) -> Any:
        """Run."""
        # dump the user using our json encoder and then load it back up as a dict
        # to remove unwanted field types
        user_as_json_string = current_app.json.dumps(g.user)
        return current_app.json.loads(user_as_json_string)
