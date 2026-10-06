"""Shared try/except helper so risky calls never crash the app.

Owned by: Ismail Muhammed  |  Branch: feature/error-handling
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

from .exceptions import (
    AIServiceError,
    DuplicateStudentError,
    EmailServiceError,
    FileOperationError,
    StudentManagementError,
    StudentNotFoundError,
    ValidationError,
)


def friendly_message(error: BaseException) -> str:
    """Turn an exception into a short message suitable for the screen."""
    if isinstance(error, DuplicateStudentError):
        return str(error) or "That student ID is already in the register."
    if isinstance(error, StudentNotFoundError):
        return str(error) or "No student was found with that ID."
    if isinstance(error, ValidationError):
        return str(error) or "Please correct the highlighted fields and try again."
    if isinstance(error, FileOperationError):
        return str(error) or "The student file could not be read or saved. Check that students.csv is not open in another program."
    if isinstance(error, AIServiceError):
        return str(error) or "The AI assistant is unavailable right now. Check the Gemini API key and try again."
    if isinstance(error, EmailServiceError):
        return str(error) or "The email could not be sent. Check the Gmail address and app password."
    if isinstance(error, StudentManagementError):
        return str(error)
    return "Something unexpected happened, but the app is still running. Please try again."


def safe_action(
    func: Callable[..., Any],
    *args: Any,
    default: Any = None,
    **kwargs: Any,
) -> Tuple[bool, Any, Optional[str]]:
    """Run a risky action and return (ok, result, error_message).

    File reads, file writes, Gemini calls, and email sends should all go
    through this helper so a failure shows a friendly message instead of
    crashing Streamlit.
    """
    try:
        return True, func(*args, **kwargs), None
    except Exception as exc:  # noqa: BLE001 - we intentionally catch all here
        return False, default, friendly_message(exc)
