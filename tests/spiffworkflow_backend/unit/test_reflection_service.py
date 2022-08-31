"""Process Model."""
from typing import Any, Callable, Dict, List, Optional

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

def test_can_describe_sample_params(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    _test_param_descs("Sample Params", [
        NoParams,
        ParamWithNoAnnotation,
        ParamWithStrAnnotation,
        ParamWithOptionalStrAnnotation,
        ParamWithDefaultValue,
        ParamWithOptionalStrAnnotationAndDefaultValue,
        ParamWithOptionalDictAnnotation,
        ParamWithOptionalListAnnotation,
        #ParamWithOptionalBuiltinListAnnotation,
    ])

def test_can_describe_airflow_operator_params(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    _test_param_descs("Mock Airflow Operators", [
        FTPSensor,
        HTTPSensor,
        ImapAttachmentSensor,
        SlackAPIFileOperator,
        #SlackWebhookOperator,
    ])

def _test_param_descs(desc, test_classes):
    test_cases = [(tc.__init__, tc.expected) for tc in test_classes]
    for i, (c, expected) in enumerate(test_cases):
        test_case_desc = f"{desc} #{i}"
        actual = ReflectionService.callable_params_desc(c)
        assert len(actual) == len(expected), test_case_desc

        for i, (actual, expected) in enumerate(zip(actual, expected)):
            test_desc = f"{test_case_desc}:{i}"
            assert actual['id'] == expected[0], test_desc
            assert actual['type'] == expected[1], test_desc
            assert actual['required'] == expected[2], test_desc

# Granular Param Testing

class NoParams:
    def __init__(): pass
    expected = []

class ParamWithNoAnnotation:
    def __init__(bob): pass
    expected = [('bob', 'any', True)]

class ParamWithStrAnnotation:
    def __init__(bob: str): pass
    expected = [('bob', 'str', True)]

class ParamWithOptionalStrAnnotation:
    def __init__(filename: Optional[str]): pass
    expected = [('filename', 'str', False)]

class ParamWithDefaultValue:
    def __init__(bob: int=33): pass
    expected = [('bob', 'int', False)]

class ParamWithOptionalStrAnnotationAndDefaultValue:
    def __init__(bob: Optional[str]='sam'): pass
    expected = [('bob', 'str', False)]

class ParamWithOptionalDictAnnotation:
    def __init__(ok: Optional[Dict]): pass
    expected = [('ok', 'any', False)]

class ParamWithOptionalListAnnotation:
    def __init__(ok: Optional[List]): pass
    expected = [('ok', 'any', False)]

class ParamWithOptionalBuiltinListAnnotation:
    def __init__(ok: Optional[list]): pass
    expected = [('ok', 'any', False)]
    
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

class ImapAttachmentSensor:
    def __init__(
        self,
        *,
        attachment_name,
        check_regex=False,
        mail_folder='INBOX',
        mail_filter='All',
        conn_id='imap_default',
        **kwargs,
    ) -> None:
        return None

    expected = [
        ('attachment_name', 'any', True),
        ('check_regex', 'any', False),
        ('mail_folder', 'any', False),
        ('mail_filter', 'any', False),
        ('conn_id', 'any', False),
    ]

class SlackAPIFileOperator:
    def __init__(
        self,
        channel: str = '#general',
        initial_comment: str = 'No message has been set!',
        filename: Optional[str] = None,
        filetype: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs,
    ) -> None:
        return None

    expected = [
        ('channel', 'str', False),
        ('initial_comment', 'str', False),
        ('filename', 'str', False),
        ('filetype', 'str', False),
        ('content', 'str', False),
    ]

class SlackWebhookOperator:
    def __init__(
        self,
        *,
        http_conn_id: str,
        webhook_token: Optional[str] = None,
        message: str = "",
        attachments: Optional[list] = None,
        blocks: Optional[list] = None,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        link_names: bool = False,
        proxy: Optional[str] = None,
        **kwargs,
    ) -> None:
        return None

    expected = [
        ('http_conn_id', 'str', True),
        ('webhook_token', 'str', False),
        ('message', 'str', False),
        ('attachments', 'any', False),
        ('blocks', 'any', False),
        ('channel', 'str', False),
        ('username', 'str', False),
        ('icon_emoji', 'str', False),
        ('icon_url', 'str', False),
        ('link_names', 'bool', False),
        ('proxy', 'str', False),
    ]
