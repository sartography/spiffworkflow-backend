"""Process Model."""
from flask.app import Flask

from spiffworkflow_backend.services.discovery_service import DiscoveryService

def test_can_discover_base_test(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    import tests.spiffworkflow_backend

    haystack = DiscoveryService.classes_in_pkg(tests.spiffworkflow_backend)
    found = [name for name, clz in haystack if name == 'BaseTest']
    assert len(found) == 1

def test_can_discover_classes_of_type_base_test(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    import tests.spiffworkflow_backend
    from tests.spiffworkflow_backend.helpers.base_test import BaseTest

    found = DiscoveryService.classes_of_type_in_pkg(tests.spiffworkflow_backend, type(BaseTest))
    assert len(list(found)) > 1
