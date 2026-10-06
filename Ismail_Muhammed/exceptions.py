"""Custom exceptions for the Student Management System.

Owned by: Ismail Muhammed  |  Branch: feature/error-handling
"""


class StudentManagementError(Exception):
    """Base class for expected, user-facing application errors."""


class ConcurrentUpdateError(StudentManagementError):
    """Another user changed the record after it was displayed."""


class DuplicateStudentError(StudentManagementError):
    """Raised when a student ID already exists in the register."""


class StudentNotFoundError(StudentManagementError):
    """Raised when a lookup, edit, or delete cannot find the ID."""


class ValidationError(StudentManagementError):
    """Raised when form input fails a regex check."""


class FileOperationError(StudentManagementError):
    """Raised when CSV read/write fails."""


class AIServiceError(StudentManagementError):
    """Raised when the Gemini request cannot be completed."""


class EmailServiceError(StudentManagementError):
    """Raised when the grade-report email cannot be sent."""
