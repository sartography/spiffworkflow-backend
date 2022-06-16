"""Test_file."""
from spiffworkflow_backend.models.file import File


def test_files_can_be_sorted() -> None:
    """Test_files_can_be_sorted."""
    europe = create_test_file(type="bpmn", name="europe")
    asia = create_test_file(type="bpmn", name="asia")
    africa = create_test_file(type="dmn", name="africa")
    oceania = create_test_file(type="dmn", name="oceania")

    mylist = [europe, oceania, asia, africa]
    assert sorted(mylist) == [asia, europe, africa, oceania]


def create_test_file(type: str, name: str):
    """Create_test_file."""
    return File(
        type=type,
        name=name,
        content_type=type,
        document={},
        last_modified="Tuesday",
        size="1",
    )