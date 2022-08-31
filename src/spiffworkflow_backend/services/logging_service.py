"""Logging_service."""
import json
import logging
import os
import sys
from typing import Any
from typing import Optional

from flask.app import Flask


# flask logging formats:
#   from: https://www.askpython.com/python-modules/flask/flask-logging
# %(asctime)s— The timestamp as a string.
# %(levelname)s—The logging level as a string.
# %(name)s—The logger name as a string.
# %(threadname)s—The thread name as a string.
# %(message)s—The log message.

# full message list:
# {'name': 'gunicorn.error', 'msg': 'GET /admin/token', 'args': (), 'levelname': 'DEBUG', 'levelno': 10, 'pathname': '~/.cache/pypoetry/virtualenvs/spiffworkflow-backend-R_hdWfN1-py3.10/lib/python3.10/site-packages/gunicorn/glogging.py', 'filename': 'glogging.py', 'module': 'glogging', 'exc_info': None, 'exc_text': None, 'stack_info': None, 'lineno': 267, 'funcName': 'debug', 'created': 1657307111.4513023, 'msecs': 451.30228996276855, 'relativeCreated': 1730.785846710205, 'thread': 139945864087360, 'threadName': 'MainThread', 'processName': 'MainProcess', 'process': 2109561, 'message': 'GET /admin/token', 'asctime': '2022-07-08T15:05:11.451Z'}

# originally from https://stackoverflow.com/a/70223539/6090676
class JsonFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """

    def __init__(
        self,
        fmt_dict: Optional[dict] = None,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        """__init__."""
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """Overwritten to look for the attribute in the format dict values instead of the fmt string."""
        return "asctime" in self.fmt_dict.values()

    # we are overriding a method that returns a string and returning a dict, hence the Any
    def formatMessage(self, record: logging.LogRecord) -> Any:
        """Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.

        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        """
        return {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record: logging.LogRecord) -> str:
        """Mostly the same as the parent's class method.

        The difference being that a dict is manipulated and dumped as JSON instead of a string.
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


def setup_logger_for_sql_statements(app: Flask) -> None:
    """Setup_logger_for_sql_statements."""
    db_log_file_name = f"log/db_{app.env}.log"
    db_handler_log_level = logging.INFO
    db_logger_log_level = logging.DEBUG
    db_handler = logging.FileHandler(db_log_file_name)
    db_handler.setLevel(db_handler_log_level)
    db_logger = logging.getLogger("sqlalchemy")
    db_logger.propagate = False
    db_logger.addHandler(db_handler)
    db_logger.setLevel(db_logger_log_level)


def setup_logger(app: Flask) -> None:
    """Setup_logger."""
    log_level = logging.DEBUG
    handlers = []

    log_formatter = logging._defaultFormatter  # type: ignore

    # the json formatter is nice for real environments but makes
    # debugging locally a little more difficult
    if app.env != "development":
        json_formatter = JsonFormatter(
            {
                "level": "levelname",
                "message": "message",
                "loggerName": "name",
                "processName": "processName",
                "processID": "process",
                "threadName": "threadName",
                "threadID": "thread",
                "timestamp": "asctime",
            }
        )
        log_formatter = json_formatter

    if os.environ.get("IS_GUNICORN") == "true":
        gunicorn_logger_error = logging.getLogger("gunicorn.error")
        log_level = gunicorn_logger_error.level
        ghandler = gunicorn_logger_error.handlers[0]
        ghandler.setFormatter(log_formatter)
        handlers.append(ghandler)

        gunicorn_logger_access = logging.getLogger("gunicorn.access")
        log_level = gunicorn_logger_access.level
        ghandler = gunicorn_logger_access.handlers[0]
        ghandler.setFormatter(log_formatter)
        handlers.append(ghandler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    handler.setFormatter(log_formatter)
    handlers.append(handler)

    logging.basicConfig(handlers=handlers)

    setup_logger_for_sql_statements(app)

    spiff_logger = logging.getLogger('spiff.metrics')
    spiff_logger.setLevel(logging.DEBUG)
    # spiff_logger_handler = logging.StreamHandler(sys.stdout)
    spiff_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s | %(action)s | %(task_type)s | %(process)s | %(processName)s')
    # spiff_logger_handler.setFormatter(spiff_formatter)
    # fh = logging.FileHandler('test.log')
    # spiff_logger_handler.setLevel(logging.DEBUG)
    # spiff_logger.addHandler(spiff_logger_handler)
    db_handler = DBHandler()
    db_handler.setLevel(logging.DEBUG)
    db_handler.setFormatter(spiff_formatter)
    spiff_logger.addHandler(db_handler)


class DBHandler(logging.Handler):

    def emit(self, record):
        print(record.process)
