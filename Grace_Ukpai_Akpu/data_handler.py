"""Read and write students.csv using Python's built-in csv module.

Owned by: Grace Ukpai Akpu  |  Branch: feature/file-handling
"""

from __future__ import annotations

import csv
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List
from filelock import FileLock, Timeout

from Ismail_Muhammed.exceptions import FileOperationError
from Great_Joseph.validate import validate_student_fields

FIELDNAMES = ["student_id", "name", "email", "phone", "course", "grade"]


@contextmanager
def register_lock(filepath: str | Path):
    """Serialize complete transactions across app sessions and processes."""
    path = Path(filepath).resolve()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(path) + ".lock", timeout=10):
            yield
    except Timeout as exc:
        raise FileOperationError("The register is busy. Please try again in a few seconds.") from exc
    except OSError as exc:
        raise FileOperationError("Cannot access the register. Check folder permissions and close the CSV in other programs.") from exc


def _read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_rows(path, [])
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is not None and reader.fieldnames != FIELDNAMES:
            raise FileOperationError("CSV headers do not match the student register format.")
        rows: List[Dict[str, str]] = []
        for index, raw in enumerate(reader, start=2):
            if None in raw:
                raise FileOperationError(f"Row {index} has extra columns.")
            if not raw or not any((value or "").strip() for value in raw.values()):
                continue
            row = {field: (raw.get(field) or "").strip() for field in FIELDNAMES}
            if not row["student_id"]:
                raise FileOperationError(f"Row {index} in {path.name} is missing a student ID.")
            valid, errors = validate_student_fields(**row)
            if not valid:
                raise FileOperationError(f"Row {reader.line_num} in {path.name}: " + " ".join(errors.values()))
            rows.append(row)
        return rows


def _write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in FIELDNAMES})
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load_from_file(filepath: str | Path) -> List[Dict[str, str]]:
    """Load every student row from CSV. Returns [] if the file is new/empty."""
    path = Path(filepath)
    try:
        return _read_rows(path)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise FileOperationError("Cannot read students.csv. Check its encoding, format and file permissions.") from exc


def save_to_file(filepath: str | Path, rows: List[Dict[str, str]]) -> None:
    """Overwrite the CSV with the current in-memory student list."""
    path = Path(filepath)
    try:
        _write_rows(path, rows)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise FileOperationError("Cannot save students.csv. Close it in other programs and check folder permissions.") from exc
