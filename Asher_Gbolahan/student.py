"""Student entity with encapsulated fields.

Owned by: Asher Gbolahan  |  Branch: feature/student-class
"""

from __future__ import annotations

from typing import Dict


class Student:
    """One student record. Attributes stay private; callers use getters/setters."""

    PASS_MARK = 50.0

    def __init__(
        self,
        student_id: str,
        name: str,
        email: str,
        phone: str,
        course: str,
        grade: str | float,
    ) -> None:
        self._student_id = str(student_id).strip()
        self._name = str(name).strip()
        self._email = str(email).strip()
        self._phone = str(phone).strip()
        self._course = str(course).strip()
        self._grade = float(grade)

    def get_student_id(self) -> str:
        return self._student_id

    def get_name(self) -> str:
        return self._name

    def get_email(self) -> str:
        return self._email

    def get_phone(self) -> str:
        return self._phone

    def get_course(self) -> str:
        return self._course

    def get_grade(self) -> float:
        return self._grade

    def set_name(self, name: str) -> None:
        self._name = name.strip()

    def set_email(self, email: str) -> None:
        self._email = email.strip()

    def set_phone(self, phone: str) -> None:
        self._phone = phone.strip()

    def set_course(self, course: str) -> None:
        self._course = course.strip()

    def set_grade(self, grade: str | float) -> None:
        self._grade = float(grade)

    def letter_grade(self) -> str:
        score = self._grade
        if score >= 70:
            return "A"
        if score >= 60:
            return "B"
        if score >= 50:
            return "C"
        if score >= 45:
            return "D"
        if score >= 40:
            return "E"
        return "F"

    def is_failing(self) -> bool:
        return self._grade < self.PASS_MARK

    def standing(self) -> str:
        return "At risk" if self.is_failing() else "In good standing"

    def to_dict(self) -> Dict[str, str]:
        return {
            "student_id": self._student_id,
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "course": self._course,
            "grade": f"{self._grade:.1f}".rstrip("0").rstrip("."),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Student":
        return cls(
            student_id=data.get("student_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            course=data.get("course", ""),
            grade=data.get("grade", "0"),
        )
