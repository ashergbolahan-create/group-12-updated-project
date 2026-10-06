"""Exception handling owned by Ismail Muhammed."""

from .exceptions import (
    DuplicateStudentError,
    StudentNotFoundError,
    ValidationError,
    FileOperationError,
    AIServiceError,
    EmailServiceError,
)
from .safe_action import friendly_message, safe_action

__all__ = [
    "DuplicateStudentError",
    "StudentNotFoundError",
    "ValidationError",
    "FileOperationError",
    "AIServiceError",
    "EmailServiceError",
    "safe_action",
    "friendly_message",
]
