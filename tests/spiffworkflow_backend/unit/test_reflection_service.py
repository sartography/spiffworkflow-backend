"""Process Model."""
from typing import Any, Callable, Dict, Optional

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

def test_can_describe_bobs_params(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    def bob(sam:str) -> None:
        return None

    param_descs = ReflectionService.callable_params_desc(bob)
    assert len(param_descs) == 1

    assert param_descs[0]['id'] == 'sam'
    assert param_descs[0]['type'] == 'str'
    assert param_descs[0]['required'] == True

def test_can_describe_airflow_operators(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    operators = [
        FTPSensor,
        HTTPSensor,
    ]
    test_cases = [(op.__init__, op.expected) for op in operators]

    for i, (c, expected) in enumerate(test_cases):
        test_case_desc = f"Test #{i}"
        actual = ReflectionService.callable_params_desc(c)
        assert len(actual) == len(expected), test_case_desc

        for i, (actual, expected) in enumerate(zip(actual, expected)):
            test_desc = f"{test_case_desc}:{i}"
            assert actual['id'] == expected[0], test_desc
            assert actual['type'] == expected[1], test_desc
            assert actual['required'] == expected[2], test_desc

# mock airflow providers

class FTPSensor:
    def __init__(self, *, 
            path: str, ftp_conn_id: str = 'ftp_default', fail_on_transient_errors: bool = True, 
            **kwargs) -> None:
        return None

    expected = [
            ('path', 'str', True), 
            ('ftp_conn_id', 'str', False), 
            ('fail_on_transient_errors', 'bool', False)
    ]

class HTTPSensor:
    def __init__(
        self,
        *,
        endpoint: str,
        http_conn_id: str = 'http_default',
        method: str = 'GET',
        request_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        response_check: Optional[Callable[..., bool]] = None,
        extra_options: Optional[Dict[str, Any]] = None,
        tcp_keep_alive: bool = True,
        tcp_keep_alive_idle: int = 120,
        tcp_keep_alive_count: int = 20,
        tcp_keep_alive_interval: int = 30,
        **kwargs: Any,
    ) -> None:
        return None

    expected = [
        ('endpoint', 'str', True),
        ('http_conn_id', 'str', False),
        ('method', 'str', False),
        ('request_params', 'any', False),
        ('headers', 'any', False),
        ('response_check', 'any', False),
        ('extra_options', 'any', False),
        ('tcp_keep_alive', 'bool', False),
        ('tcp_keep_alive_idle', 'int', False),
        ('tcp_keep_alive_count', 'int', False),
        ('tcp_keep_alive_interval', 'int', False),
    ] 
