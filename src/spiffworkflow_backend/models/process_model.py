"""Process_model."""
import marshmallow
from marshmallow import post_load
from marshmallow import Schema

from dataclasses import dataclass
from dataclasses import field
from typing import Optional


@dataclass(order=True)
class ProcessModelInfo:
    """ProcessModelInfo."""

    sort_index: str = field(init=False)

    id: str
    display_name: str
    description: str
    is_master_spec: Optional[bool] = False
    standalone: Optional[bool] = False
    library: Optional[bool] = False
    primary_file_name: Optional[str] = ""
    primary_process_id: Optional[str] = ""
    libraries: Optional[list[str]] = field(default_factory=list)
    process_group_id: Optional[str] = ""
    display_order: Optional[int] = 0
    is_review: Optional[bool] = False
    files: Optional[list[str]] = field(default_factory=list)

    def __post_init__(self):
        """__post_init__."""
        self.sort_index = f"{self.process_group_id}:{self.id}"

    def __eq__(self, other):
        """__eq__."""
        if not isinstance(other, ProcessModelInfo):
            return False
        if other.id == self.id:
            return True
        return False


class ProcessModelInfoSchema(Schema):
    """ProcessModelInfoSchema."""

    class Meta:
        """Meta."""

        model = ProcessModelInfo

    id = marshmallow.fields.String(required=True)
    display_name = marshmallow.fields.String(required=True)
    description = marshmallow.fields.String()
    is_master_spec = marshmallow.fields.Boolean(required=True)
    standalone = marshmallow.fields.Boolean(required=True)
    library = marshmallow.fields.Boolean(required=True)
    display_order = marshmallow.fields.Integer(allow_none=True)
    primary_file_name = marshmallow.fields.String(allow_none=True)
    primary_process_id = marshmallow.fields.String(allow_none=True)
    is_review = marshmallow.fields.Boolean(allow_none=True)
    process_group_id = marshmallow.fields.String(allow_none=True)
    libraries = marshmallow.fields.List(marshmallow.fields.String(), allow_none=True)
    files = marshmallow.fields.List(marshmallow.fields.Nested("FileSchema"))

    @post_load
    def make_spec(self, data, **kwargs):
        """Make_spec."""
        return ProcessModelInfo(**data)
