"""
Error Reporting Utility

This module provides enhanced error reporting capabilities with context
tracking, structured logging, and error aggregation. It's designed to make
debugging easier by providing more context around errors.
"""

import logging
import traceback
import time
import uuid
import json
import os
import sys
from functools import wraps
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from django.conf import settings
from threading import local

# Initialize logger
logger = logging.getLogger("django")

# Thread local storage for error context
_local = local()

# Enable detailed error tracking
DETAILED_ERRORS = getattr(settings, "DETAILED_ERROR_REPORTING", True)


def initialize_error_context():
    """Initialize the thread-local error context."""
    _local.error_context = {
        "request_id": str(uuid.uuid4())[:8],
        "start_time": time.time(),
        "breadcrumbs": [],
        "tags": {},
        "extra": {},
    }


def get_error_context() -> Dict[str, Any]:
    """Get the current error context or initialize if needed."""
    if not hasattr(_local, "error_context"):
        initialize_error_context()
    return _local.error_context


def add_breadcrumb(
    message: str,
    category: str = "info",
    level: str = "info",
    data: Optional[Dict] = None,
):
    """
    Add a breadcrumb to the error context.

    Breadcrumbs track the sequence of events leading up to an error, making it easier
    to understand what happened before the error occurred.

    Args:
        message: Description of the event
        category: Category of the event (e.g., "db", "http", "ui")
        level: Severity level (debug, info, warning, error)
        data: Additional contextual data
    """
    context = get_error_context()
    breadcrumb = {
        "timestamp": time.time(),
        "message": message,
        "category": category,
        "level": level,
        "data": data or {},
    }
    context["breadcrumbs"].append(breadcrumb)

    # Keep only the last 20 breadcrumbs to avoid memory buildup
    if len(context["breadcrumbs"]) > 20:
        context["breadcrumbs"] = context["breadcrumbs"][-20:]


def add_tag(key: str, value: str):
    """
    Add a tag to the error context.

    Tags are key-value pairs that provide high-level information about the error context,
    such as environment, user ID, or transaction ID.

    Args:
        key: Tag key
        value: Tag value
    """
    context = get_error_context()
    context["tags"][key] = value


def add_extra(key: str, value: Any):
    """
    Add extra data to the error context.

    Extra data provides additional contextual information that might be useful
    for debugging, such as request parameters, response data, or state information.

    Args:
        key: Extra data key
        value: Extra data value
    """
    context = get_error_context()
    context["extra"][key] = value


def calculate_duration() -> float:
    """Calculate the duration since the context was initialized."""
    context = get_error_context()
    return time.time() - context["start_time"]


def format_error_context() -> Dict[str, Any]:
    """Format the error context for structured logging."""
    context = get_error_context()
    duration = calculate_duration()

    return {
        "request_id": context["request_id"],
        "duration": f"{duration:.2f}s",
        "tags": context["tags"],
        "extra": context["extra"],
        "breadcrumbs": (
            context["breadcrumbs"]
            if DETAILED_ERRORS
            else f"{len(context['breadcrumbs'])} breadcrumbs"
        ),
    }


def log_error(error: Exception, message: str = None, include_traceback: bool = True):
    """
    Log an error with enhanced context.

    This function logs an error with all the contextual information that has been
    gathered, making it easier to understand the state of the application when
    the error occurred.

    Args:
        error: The exception object
        message: Optional custom error message
        include_traceback: Whether to include the traceback in the log
    """
    context = get_error_context()
    error_message = message or str(error)
    duration = calculate_duration()

    error_data = {
        "message": error_message,
        "exception": {"type": error.__class__.__name__, "value": str(error)},
        "context": format_error_context(),
    }

    if include_traceback:
        error_data["traceback"] = traceback.format_exc()

    try:
        # Try JSON formatting for structured logging
        error_json = json.dumps(error_data)
        logger.error(
            f"❌ ERROR [{context['request_id']}]: {error_message} (took {duration:.2f}s)"
        )
        logger.error(f"📊 Context: {error_json}")
    except (TypeError, ValueError):
        # Fall back to simpler logging if JSON serialization fails
        logger.error(
            f"❌ ERROR [{context['request_id']}]: {error_message} (took {duration:.2f}s)"
        )
        if include_traceback:
            logger.error(f"📊 Traceback: {traceback.format_exc()}")

    # Always log the raw exception with traceback for Django's error reporting
    logger.exception(error)


def error_handling_decorator(func):
    """
    Decorator to add error tracking and logging to a function.

    This decorator initializes the error context, adds a breadcrumb for the function call,
    and logs any errors that occur during execution.

    Usage:
        @error_handling_decorator
        def my_function(arg1, arg2):
            # Function implementation
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        initialize_error_context()
        add_breadcrumb(
            message=f"Calling {func.__name__}",
            category="function",
            level="info",
            data={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
        )

        try:
            result = func(*args, **kwargs)
            add_breadcrumb(
                message=f"Completed {func.__name__}", category="function", level="info"
            )
            return result
        except Exception as e:
            log_error(e, message=f"Error in {func.__name__}")
            raise

    return wrapper


def log_warning(message: str, data: Optional[Dict] = None):
    """
    Log a warning with enhanced context.

    Args:
        message: Warning message
        data: Additional contextual data
    """
    context = get_error_context()
    add_breadcrumb(message, category="warning", level="warning", data=data)

    logger.warning(f"⚠ {message}")
    if data:
        try:
            logger.warning(f"📊 Data: {json.dumps(data)}")
        except (TypeError, ValueError):
            logger.warning(f"📊 Data: {str(data)}")


def log_info(message: str, data: Optional[Dict] = None):
    """
    Log an info message with enhanced context.

    Args:
        message: Info message
        data: Additional contextual data
    """
    context = get_error_context()
    add_breadcrumb(message, category="info", level="info", data=data)

    logger.info(f"ℹ {message}")
    if DETAILED_ERRORS and data:
        try:
            logger.info(f"📊 Data: {json.dumps(data)}")
        except (TypeError, ValueError):
            logger.info(f"📊 Data: {str(data)}")


class ErrorTracker:
    """
    Context manager for tracking errors in a block of code.

    This class provides a context manager that initializes error context,
    adds breadcrumbs for entry and exit, and logs any errors that occur.

    Usage:
        with ErrorTracker("Processing user request"):
            # Code that might raise exceptions
    """

    def __init__(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        self.operation_name = operation_name
        self.tags = tags or {}

    def __enter__(self):
        initialize_error_context()
        context = get_error_context()

        # Add operation info to context
        for key, value in self.tags.items():
            add_tag(key, value)

        add_breadcrumb(
            message=f"Starting {self.operation_name}",
            category="operation",
            level="info",
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log_error(exc_val, message=f"Error in {self.operation_name}")
            return False  # Don't suppress the exception

        add_breadcrumb(
            message=f"Completed {self.operation_name}",
            category="operation",
            level="info",
            data={"duration": f"{calculate_duration():.2f}s"},
        )

        return False  # Don't suppress exceptions

    def add_context(self, key: str, value: Any):
        """Add extra context data during execution."""
        add_extra(key, value)
        return self


# Helper function to make error context available in templates
def get_error_context_for_template():
    """Get error context formatted for template rendering."""
    context = get_error_context()
    return {
        "request_id": context["request_id"],
        "breadcrumbs": context["breadcrumbs"],
        "tags": context["tags"],
        "extra": context["extra"],
    }
