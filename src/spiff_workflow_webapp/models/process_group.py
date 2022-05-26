"""Process_group."""
from marshmallow import Schema, post_load


# class ProcessGroupModel(db.Model):  # type: ignore
#     """ProcessGroupMode."""
#
#     __tablename__ = "process_group"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))


class ProcessGroup:
    """ProcessGroup."""

    def __init__(self, id, display_name, display_order=0, admin=False):
        """__init__."""
        self.id = (
            id  # A unique string name, lower case, under scores (ie, 'my_group')
        )
        self.display_name = display_name
        self.display_order = display_order
        self.admin = admin
        self.workflows = []  # For storing Workflow Metadata
        self.specs = []  # For the list of specifications associated with a group
        self.meta = None  # For storing group metadata

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
        fields = ["id", "display_name", "display_order", "admin"]

    @post_load
    def make_cat(self, data, **kwargs):
        """Make_cat."""
        return ProcessGroup(**data)
