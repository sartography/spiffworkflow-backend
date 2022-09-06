"""Process Model."""
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from flask.app import Flask

from spiffworkflow_backend.services.reflection_service import ReflectionService


def test_can_find_base_test(app: Flask, with_db_and_bpmn_file_cleanup: None) -> None:
    import tests.spiffworkflow_backend

    haystack = ReflectionService.classes_in_pkg(tests.spiffworkflow_backend)
    found = [name for name, clz in haystack if name == "BaseTest"]
    assert len(found) == 1


def test_can_find_classes_of_type_base_test(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    import tests.spiffworkflow_backend
    from tests.spiffworkflow_backend.helpers.base_test import BaseTest

    found = ReflectionService.classes_of_type_in_pkg(
        tests.spiffworkflow_backend, type(BaseTest)
    )
    assert len(list(found)) > 1


def test_can_describe_sample_params(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    _test_param_descs(
        "Sample Params",
        [
            NoParams,
            ParamWithNoAnnotation,
            ParamWithStrAnnotation,
            ParamWithOptionalStrAnnotation,
            ParamWithDefaultValue,
            ParamWithOptionalStrAnnotationAndDefaultValue,
            ParamWithOptionalDictAnnotation,
            ParamWithOptionalListAnnotation,
            ParamWithOptionalBuiltinListAnnotation,
        ],
    )


def test_can_describe_airflow_operator_params(
    app: Flask, with_db_and_bpmn_file_cleanup: None
) -> None:
    _test_param_descs(
        "Mock Airflow Operators",
        [
            FTPSensor,
            HTTPSensor,
            ImapAttachmentSensor,
            SlackAPIFileOperator,
            SlackWebhookOperator,
        ],
    )


def _test_param_descs(desc: str, test_classes: list[Callable]) -> None:
    test_cases = [(tc.__init__, tc.expected) for tc in test_classes]  # type: ignore
    for i, (c, tc_expected) in enumerate(test_cases):
        test_case_desc = f"{desc} #{i}"
        tc_actual = ReflectionService.callable_params_desc(c)
        assert len(tc_actual) == len(tc_expected), test_case_desc  # type: ignore

        for i, (actual, expected) in enumerate(zip(tc_actual, tc_expected)):
            test_desc = f"{test_case_desc}:{i}"
            assert actual["id"] == expected[0], test_desc
            assert actual["type"] == expected[1], test_desc
            assert actual["required"] == expected[2], test_desc


# Granular Param Testing


class NoParams:
    """docstring."""

    def __init__(self) -> None:
        """docstring."""
        pass

    expected = []  # type: ignore


class ParamWithNoAnnotation:
    """docstring."""

    def __init__(self, bob):  # type: ignore
        """docstring."""
        pass

    expected = [("bob", "any", True)]


class ParamWithStrAnnotation:
    """docstring."""

    def __init__(self, bob: str):
        """docstring."""
        pass

    expected = [("bob", "str", True)]


class ParamWithOptionalStrAnnotation:
    """docstring."""

    def __init__(self, filename: Optional[str]):
        """docstring."""
        pass

    expected = [("filename", "str", False)]


class ParamWithDefaultValue:
    """docstring."""

    def __init__(self, bob: int = 33):
        """docstring."""
        pass

    expected = [("bob", "int", False)]


class ParamWithOptionalStrAnnotationAndDefaultValue:
    """docstring."""

    def __init__(self, bob: Optional[str] = "sam"):
        """docstring."""
        pass

    expected = [("bob", "str", False)]


class ParamWithOptionalDictAnnotation:
    """docstring."""

    def __init__(self, ok: Optional[Dict]):
        """docstring."""
        pass

    expected = [("ok", "any", False)]


class ParamWithOptionalListAnnotation:
    """docstring."""

    def __init__(self, ok: Optional[List]):
        """docstring."""
        pass

    expected = [("ok", "any", False)]


class ParamWithOptionalBuiltinListAnnotation:
    """docstring."""

    def __init__(self, ok: Optional[list]):
        """docstring."""
        pass

    expected = [("ok", "any", False)]


# mock airflow providers


class FTPSensor:
    """docstring."""

    def __init__(  # type: ignore
        self,
        *,
        path: str,
        ftp_conn_id: str = "ftp_default",
        fail_on_transient_errors: bool = True,
        **kwargs,
    ) -> None:
        """docstring."""
        return None

    expected = [
        ("path", "str", True),
        ("ftp_conn_id", "str", False),
        ("fail_on_transient_errors", "bool", False),
    ]


class HTTPSensor:
    """docstring."""

    def __init__(
        self,
        *,
        endpoint: str,
        http_conn_id: str = "http_default",
        method: str = "GET",
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
        """docstring."""
        return None

    expected = [
        ("endpoint", "str", True),
        ("http_conn_id", "str", False),
        ("method", "str", False),
        ("request_params", "any", False),
        ("headers", "any", False),
        ("response_check", "any", False),
        ("extra_options", "any", False),
        ("tcp_keep_alive", "bool", False),
        ("tcp_keep_alive_idle", "int", False),
        ("tcp_keep_alive_count", "int", False),
        ("tcp_keep_alive_interval", "int", False),
    ]


class ImapAttachmentSensor:
    """docstring."""

    def __init__(  # type: ignore
        self,
        *,
        attachment_name,
        check_regex=False,
        mail_folder="INBOX",
        mail_filter="All",
        conn_id="imap_default",
        **kwargs,
    ) -> None:
        """docstring."""
        return None

    expected = [
        ("attachment_name", "any", True),
        ("check_regex", "any", False),
        ("mail_folder", "any", False),
        ("mail_filter", "any", False),
        ("conn_id", "any", False),
    ]


class SlackAPIFileOperator:
    """docstring."""

    def __init__(  # type: ignore
        self,
        channel: str = "#general",
        initial_comment: str = "No message has been set!",
        filename: Optional[str] = None,
        filetype: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs,
    ) -> None:
        """docstring."""
        return None

    expected = [
        ("channel", "str", False),
        ("initial_comment", "str", False),
        ("filename", "str", False),
        ("filetype", "str", False),
        ("content", "str", False),
    ]


class SlackWebhookOperator:
    """docstring."""

    def __init__(  # type: ignore
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
        """docstring."""
        return None

    expected = [
        ("http_conn_id", "str", True),
        ("webhook_token", "str", False),
        ("message", "str", False),
        ("attachments", "any", False),
        ("blocks", "any", False),
        ("channel", "str", False),
        ("username", "str", False),
        ("icon_emoji", "str", False),
        ("icon_url", "str", False),
        ("link_names", "bool", False),
        ("proxy", "str", False),
    ]
