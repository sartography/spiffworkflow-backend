"""Logging_service."""
import json
import logging
import os

from flask.app import Flask


# originally from https://stackoverflow.com/a/70223539/6090676
class JsonFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """

    def __init__(
        self,
        fmt_dict: dict = None,
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

    def formatMessage(self, record) -> dict:
        """Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.

        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        """
        return {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record) -> str:
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


# formats:
#   from: https://www.askpython.com/python-modules/flask/flask-logging
# %(asctime)s— The timestamp as a string.
# %(levelname)s—The logging level as a string.
# %(name)s—The logger name as a string.
# %(threadname)s—The thread name as a string.
# %(message)s—The log message.
def setup_logger(app: Flask) -> None:
    """Setup_logger."""
    server_log_file_name = f"log/server_{app.env}.log"

    log_level = logging.DEBUG
    handlers = []

    if os.environ.get("IS_GUNICORN") == "true":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        log_level = gunicorn_logger.level
        handlers.extend(gunicorn_logger.handlers)

    handler = logging.FileHandler(server_log_file_name)
    handler.setLevel(log_level)

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

    handler.setFormatter(json_formatter)
    handlers.append(handler)
    logging.basicConfig(handlers=handlers)

    setup_logger_for_sql_statements(app)
