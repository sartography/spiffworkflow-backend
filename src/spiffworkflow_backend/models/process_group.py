"""Process_group."""
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

import marshmallow
from marshmallow import post_load
from marshmallow import Schema

from spiffworkflow_backend.models.process_model import ProcessModelInfo


@dataclass(order=True)
class ProcessGroup:
    """ProcessGroup."""

    sort_index: str = field(init=False)

    id: str  # A unique string name, lower case, under scores (ie, 'my_group')
    display_name: str
    display_order: Optional[int] = 0
    admin: Optional[bool] = False
    process_models: Optional[list[ProcessModelInfo]] = field(default_factory=list)

    def __post_init__(self):
        """__post_init__."""
        self.sort_index = f"{self.display_order}:{self.id}"

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
        marshmallow.fields.Nested(
            "ProcessModelInfoSchema", dump_only=True, required=False
        )
    )

    @post_load
    def make_process_group(self, data, **kwargs):
        """Make_process_group."""
        return ProcessGroup(**data)
