"""
Logging configuration for the application.
Provides JSON-formatted structured logging with request correlation IDs.
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from contextvars import ContextVar

from app.config import settings

# Context variable to store request ID across async calls
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format.
    Includes request_id from context if available.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request_id from context if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # Add extra fields from the record
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.
    """

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logging() -> None:
    """
    Configure application-wide logging based on settings.
    """
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Choose formatter based on settings
    if settings.log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds extra fields to log records.
    Useful for adding context like email, operation, etc.
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add extra fields to the log record."""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        # Store extra fields in a way the JSONFormatter can access them
        extra_fields = kwargs['extra'].copy()
        kwargs['extra']['extra_fields'] = extra_fields

        return msg, kwargs


def get_logger_with_context(name: str, **context: Any) -> LoggerAdapter:
    """
    Get a logger with additional context fields.

    Args:
        name: Logger name
        **context: Additional fields to include in all log entries

    Returns:
        Logger adapter with context

    Example:
        logger = get_logger_with_context(__name__, email="test@example.com")
        logger.info("Checking suppression")
        # Output: {"level": "INFO", "email": "test@example.com", "message": "Checking suppression"}
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, context)


def set_request_id(request_id: str) -> None:
    """
    Set the request ID in context for the current async task.

    Args:
        request_id: Unique identifier for the current request
    """
    request_id_var.set(request_id)


def clear_request_id() -> None:
    """Clear the request ID from context."""
    request_id_var.set(None)


def get_request_id() -> str:
    """
    Get the current request ID from context.

    Returns:
        Request ID or None if not set
    """
    return request_id_var.get()
