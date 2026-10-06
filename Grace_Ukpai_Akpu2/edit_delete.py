"""Edit Student and Delete Student screens.

Owned by: Grace Ukpai Akpu  |  Branch: feature/edit-delete-ui
"""

from __future__ import annotations

import streamlit as st
import hashlib
import json

from Asher_Gbolahan.student_manager import StudentManager
from Great_Joseph.validate import format_error_list, validate_student_fields
from Ismail_Muhammed.safe_action import safe_action


def _student_options(manager: StudentManager) -> dict[str, str]:
    return {
        f"{item.get_student_id()} — {item.get_name()}": item.get_student_id()
        for item in manager.get_all()
    }


def render_edit_student(manager: StudentManager) -> None:
    options = _student_options(manager)
    if not options:
        st.info("Add a student first, then you can update their record here.")
        return

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Update a record")
    st.caption("Choose a student and update their details below.")

    label = st.selectbox("Choose a student", list(options.keys()), key="edit_picker")
    current = manager.find_student(options[label])

    prefix = f"edit_{current.get_student_id()}_"
    snapshot_key = prefix + "snapshot"
    if prefix + "name" not in st.session_state:
        st.session_state[snapshot_key] = current.to_dict()
    if st.button("Reload current record"):
        for key in list(st.session_state):
            if key.startswith(prefix):
                del st.session_state[key]
        st.rerun()

    with st.form(f"edit_student_form_{current.get_student_id()}"):
        col_a, col_b = st.columns(2)
        with col_a:
            student_id = st.text_input("Student ID", value=current.get_student_id(), disabled=True)
            name = st.text_input("Full name", value=current.get_name(), key=prefix + "name")
            email = st.text_input("Email", value=current.get_email(), key=prefix + "email")
        with col_b:
            phone = st.text_input("Phone", value=current.get_phone(), key=prefix + "phone")
            course = st.text_input("Course", value=current.get_course(), key=prefix + "course")
            grade = st.text_input("Grade (0–100)", value=str(current.get_grade()), key=prefix + "grade")
        submitted = st.form_submit_button("Save changes", width="stretch")

    if submitted:
        ok, errors = validate_student_fields(student_id, name, email, phone, course, grade)
        if not ok:
            for message in format_error_list(errors):
                st.error(message)
        else:
            success, _, error = safe_action(
                manager.edit_student, student_id, name, email, phone, course, grade,
                expected=st.session_state[snapshot_key]
            )
            if success:
                st.session_state[snapshot_key] = manager.find_student(student_id).to_dict()
                st.success(f"Updates for {name.strip()} have been saved.")
            else:
                st.error(error)
    st.markdown("</div>", unsafe_allow_html=True)


def render_delete_student(manager: StudentManager) -> None:
    if message := st.session_state.pop("delete_success", None):
        st.success(message)
    options = _student_options(manager)
    if not options:
        st.info("There is nobody to remove — the register is empty.")
        return

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Remove a student")
    st.caption("This action permanently removes the selected student.")

    label = st.selectbox("Choose a student", list(options.keys()), key="delete_picker")
    current = manager.find_student(options[label])

    st.warning(
        f"You are about to remove **{current.get_name()}** ({current.get_student_id()}) "
        f"from {current.get_course()}."
    )
    revision = hashlib.sha256(json.dumps(current.to_dict(), sort_keys=True).encode()).hexdigest()[:16]
    confirmed = st.checkbox("Yes, permanently remove this student from the register.", key=f"confirm_delete_{current.get_student_id()}_{revision}")
    if st.button("Delete student", type="primary", disabled=not confirmed, width="stretch"):
        success, _, error = safe_action(manager.delete_student, current.get_student_id(), expected=current.to_dict())
        if success:
            st.session_state["delete_success"] = f"{current.get_name()} has been removed and the file has been updated."
            st.rerun()
        else:
            st.error(error)
    st.markdown("</div>", unsafe_allow_html=True)
