"""Process_group."""
from marshmallow import post_load
from marshmallow import Schema
import marshmallow


class ProcessGroup:
    """ProcessGroup."""

    def __init__(self, id, display_name, display_order=0, admin=False, process_models=None):
        """__init__."""
        self.id = id  # A unique string name, lower case, under scores (ie, 'my_group')
        self.display_name = display_name
        self.display_order = display_order
        self.admin = admin
        self.workflows = []  # For storing Workflow Metadata
        self.meta = None  # For storing group metadata

        if process_models is None:
            process_models = []

        self.process_models = process_models  # For the list of specifications associated with a group

    def __eq__(self, other):
        """__eq__."""
        if not isinstance(other, ProcessGroup):
            return False
        if other.id == self.id:
            return True
        return False


class ProcessGroupSchema(Schema):
    """ProcessGroupSchema."""

    class Meta:
        """Meta."""

        model = ProcessGroup
        fields = ["id", "display_name", "display_order", "admin", "process_models"]

    process_models = marshmallow.fields.List(
        marshmallow.fields.Nested("ProcessModelInfoSchema", dump_only=True, required=False)
    )

    @post_load
    def make_process_group(self, data, **kwargs):
        """Make_process_group."""
        return ProcessGroup(**data)
