"""In-memory register that talks to the CSV layer.

Owned by: Asher Gbolahan  |  Branch: feature/student-class
"""

from __future__ import annotations

from pathlib import Path
from copy import deepcopy
from typing import Dict, List, Optional

from Grace_Ukpai_Akpu.data_handler import load_from_file, save_to_file, register_lock
from Great_Joseph.validate import require_valid_student_fields
from Ismail_Muhammed.exceptions import DuplicateStudentError, StudentNotFoundError, ConcurrentUpdateError

from .student import Student


class StudentManager:
    """Add, find, edit, delete, and persist Student objects."""

    def __init__(self, csv_path: str | Path) -> None:
        self._csv_path = Path(csv_path)
        self._students: Dict[str, Student] = {}
        self.load()

    def load(self) -> None:
        with register_lock(self._csv_path):
            self._load_unlocked()

    def _load_unlocked(self) -> None:
        rows = load_from_file(self._csv_path)
        loaded: Dict[str, Student] = {}
        for row in rows:
            student = Student.from_dict(row)
            if student.get_student_id().upper() in loaded:
                raise DuplicateStudentError("Duplicate student IDs found in the CSV file.")
            loaded[student.get_student_id().upper()] = student
        self._students = loaded
        self._baseline = [s.to_dict() for s in self.get_all()]

    def save(self) -> None:
        """Persist direct changes only if the saved register has not changed."""
        with register_lock(self._csv_path):
            disk = load_from_file(self._csv_path)
            normalized = [Student.from_dict(row).to_dict() for row in disk]
            if sorted(normalized, key=lambda r: r["student_id"]) != self._baseline:
                self._load_unlocked()
                raise ConcurrentUpdateError("The register changed. Refresh before saving again.")
            try:
                self._save_unlocked()
            except Exception:
                self._load_unlocked()
                raise

    def _save_unlocked(self) -> None:
        rows = [student.to_dict() for student in self.get_all()]
        for row in rows:
            require_valid_student_fields(**row)
        save_to_file(self._csv_path, rows)
        self._baseline = rows

    def _change(self, action):
        with register_lock(self._csv_path):
            self._load_unlocked()
            previous = deepcopy(self._students)
            try:
                result = action()
                self._save_unlocked()
                return result
            except Exception:
                self._students = previous
                raise

    def _check_current(self, student_id, expected):
        student = self.find_student(student_id)
        if expected is not None and student.to_dict() != expected:
            raise ConcurrentUpdateError(
                "Another user changed this student. Reopen the page to review the latest record before saving or deleting."
            )
        return student

    def add_student(
        self,
        student_id: str,
        name: str,
        email: str,
        phone: str,
        course: str,
        grade: str,
    ) -> Student:
        require_valid_student_fields(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            course=course,
            grade=grade,
        )
        def add():
            key = student_id.strip().upper()
            if key in self._students:
                raise DuplicateStudentError(f"Student ID {student_id.strip()} is already on the register. Choose a different ID.")
            student = Student(student_id, name, email, phone, course, grade)
            self._students[key] = student
            return student
        return self._change(add)

    def edit_student(
        self,
        student_id: str,
        name: str,
        email: str,
        phone: str,
        course: str,
        grade: str,
        *, expected: Optional[Dict[str, str]] = None,
    ) -> Student:
        require_valid_student_fields(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            course=course,
            grade=grade,
        )
        def edit():
            student = self._check_current(student_id, expected)
            student.set_name(name)
            student.set_email(email)
            student.set_phone(phone)
            student.set_course(course)
            student.set_grade(grade)
            return student
        return self._change(edit)

    def delete_student(self, student_id: str, *, expected: Optional[Dict[str, str]] = None) -> Student:
        def delete():
            student = self._check_current(student_id, expected)
            del self._students[student.get_student_id().upper()]
            return student
        return self._change(delete)

    def find_student(self, student_id: str) -> Student:
        key = (student_id or "").strip().upper()
        student = self._students.get(key)
        if student is None:
            raise StudentNotFoundError(f"No student found with ID {key}.")
        return student

    def get_all(self) -> List[Student]:
        return sorted(self._students.values(), key=lambda item: item.get_student_id())

    def count(self) -> int:
        return len(self._students)

    def average_grade(self) -> Optional[float]:
        students = self.get_all()
        if not students:
            return None
        return sum(item.get_grade() for item in students) / len(students)

    def at_risk(self) -> List[Student]:
        return [item for item in self.get_all() if item.is_failing()]

    def top_student(self) -> Optional[Student]:
        students = self.get_all()
        if not students:
            return None
        return max(students, key=lambda item: item.get_grade())

    def courses(self) -> List[str]:
        return sorted({item.get_course() for item in self.get_all()})
