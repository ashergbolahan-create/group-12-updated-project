"""Regex checks used by every form before a student is saved.

Owned by: Great Joseph  |  Branch: feature/regex-validation
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from Ismail_Muhammed.exceptions import ValidationError

# STU001, CSC2024, ID-104 — letters/digits with an optional hyphen, 4–12 chars.
STUDENT_ID_PATTERN = re.compile(r"^[A-Za-z]{2,5}[-]?\d{2,6}$")

# Practical email: local@domain.tld
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

# Nigerian local (0xxxxxxxxxx) or international (+234xxxxxxxxxx / 10–15 digits).
PHONE_PATTERN = re.compile(r"^(?:0\d{10}|\+\d{10,14}|\d{10,15})$")

# Whole or one-decimal grades from 0 through 100.
GRADE_PATTERN = re.compile(r"^(?:100(?:\.0)?|[0-9]{1,2}(?:\.\d)?)$")

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,59}$")
COURSE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 &/().'-]{1,59}$")


def is_valid_student_id(value: str) -> bool:
    return bool(STUDENT_ID_PATTERN.fullmatch((value or "").strip()))


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch((value or "").strip()))


def is_valid_phone(value: str) -> bool:
    cleaned = re.sub(r"[ \-()]", "", value or "")
    return bool(PHONE_PATTERN.fullmatch(cleaned))


def is_valid_grade(value: str) -> bool:
    text = (value or "").strip()
    if not GRADE_PATTERN.fullmatch(text):
        return False
    return 0.0 <= float(text) <= 100.0


def is_valid_name(value: str) -> bool:
    return bool(NAME_PATTERN.fullmatch((value or "").strip()))


def is_valid_course(value: str) -> bool:
    return bool(COURSE_PATTERN.fullmatch((value or "").strip()))


def validate_student_fields(
    student_id: str,
    name: str,
    email: str,
    phone: str,
    course: str,
    grade: str,
) -> Tuple[bool, Dict[str, str]]:
    """Return (ok, field_errors). An empty dict means every field passed."""
    errors: Dict[str, str] = {}

    if not is_valid_student_id(student_id):
        errors["student_id"] = "Use 2–5 letters plus 2–6 digits, e.g. STU001 or CSC-104."
    if not is_valid_name(name):
        errors["name"] = "Enter a full name using letters, spaces, hyphens or apostrophes."
    if not is_valid_email(email):
        errors["email"] = "Enter a valid email such as name@university.edu."
    if not is_valid_phone(phone):
        errors["phone"] = "Enter a phone number such as 08031234567 or +2348031234567."
    if not is_valid_course(course):
        errors["course"] = "Enter a course name such as Computer Science."
    if not is_valid_grade(str(grade)):
        errors["grade"] = "Grade must be a number from 0 to 100."

    return (len(errors) == 0, errors)


def require_valid_student_fields(**fields: str) -> None:
    """Raise ValidationError if any field fails. Used by StudentManager."""
    ok, errors = validate_student_fields(
        fields["student_id"],
        fields["name"],
        fields["email"],
        fields["phone"],
        fields["course"],
        fields["grade"],
    )
    if not ok:
        message = " ".join(errors.values())
        raise ValidationError(message)


def format_error_list(errors: Dict[str, str]) -> List[str]:
    return list(errors.values())
