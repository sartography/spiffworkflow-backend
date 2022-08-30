"""Process Model."""
import ast

from flask.app import Flask

from spiffworkflow_backend.services.reflection_service import ReflectionService

def test_can_find_base_test(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    import tests.spiffworkflow_backend

    haystack = ReflectionService.classes_in_pkg(tests.spiffworkflow_backend)
    found = [name for name, clz in haystack if name == 'BaseTest']
    assert len(found) == 1

def test_can_find_classes_of_type_base_test(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    import tests.spiffworkflow_backend
    from tests.spiffworkflow_backend.helpers.base_test import BaseTest

    found = ReflectionService.classes_of_type_in_pkg(tests.spiffworkflow_backend, type(BaseTest))
    assert len(list(found)) > 1

def bob(sam:str = "sue") -> None:
    return None

def test_XXX(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    #print(ast.dump(bob.__code__))
    pass

