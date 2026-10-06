"""Student Management System — Streamlit application entry point."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from Grace_Ukpai_Akpu2.edit_delete import render_delete_student, render_edit_student
from Great_Joseph2.email_service import render_email_report
from Great_Joseph2.gemini_assistant import render_ai_assistant
from Asher_Gbolahan.student_manager import StudentManager
from Asher_Gbolahan.access_control import require_access
from Ismail_Muhammed.safe_action import safe_action
from Oluwakorede_Olawoye.add_view import render_add_student, render_dashboard, render_view_students

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

CSV_PATH = ROOT / "data" / "students.csv"
STYLES = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")

PAGES = [
    "Dashboard",
    "Add Student",
    "View Students",
    "Edit Student",
    "Delete Student",
    "AI Assistant",
    "Email Reports",
    "Team & Design",
]

OWNERS = {
    "Dashboard": "Oluwakorede Olawoye",
    "Add Student": "Oluwakorede Olawoye",
    "View Students": "Oluwakorede Olawoye",
    "Edit Student": "Grace Ukpai Akpu",
    "Delete Student": "Grace Ukpai Akpu",
    "AI Assistant": "Great Joseph",
    "Email Reports": "Great Joseph",
    "Team & Design": "Asher Gbolahan · Team Lead",
}


def _manager() -> StudentManager:
    if "manager" not in st.session_state:
        ok, manager, error = safe_action(StudentManager, CSV_PATH)
        if not ok:
            st.error(error)
            st.stop()
        st.session_state.manager = manager
    else:
        ok, _, error = safe_action(st.session_state.manager.load)
        if not ok:
            st.error(error)
            st.stop()
    return st.session_state.manager


def _hero(title: str, subtitle: str, owner: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-kicker">Student Management System</div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <div class="owner-chip">Owned by {owner}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_team_page() -> None:
    st.markdown(
        """
        <div class="team-grid">
          <div class="team-card"><h3>Asher Gbolahan</h3><p>Team leader — OOP core, Student and StudentManager classes, and review coordination.</p></div>
          <div class="team-card"><h3>Grace Ukpai Akpu</h3><p>File handling — CSV load/save with utf-8 and header checks.</p></div>
          <div class="team-card"><h3>Great Joseph</h3><p>Regular expressions — ID, email, phone, name, course and grade.</p></div>
          <div class="team-card"><h3>Oluwakorede Olawoye</h3><p>Add Student form, live register table, and dashboard metrics.</p></div>
          <div class="team-card"><h3>Grace Ukpai Akpu</h3><p>Edit and Delete screens with confirmation and shared validation.</p></div>
          <div class="team-card"><h3>Ismail Muhammed</h3><p>Exception handling — custom errors and the shared safe_action helper.</p></div>
          <div class="team-card"><h3>Great Joseph</h3><p>AI integration — OpenAI and Gemini assistants, Gmail SMTP reports, and documentation.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        """
        **How the required topics appear in this build**

        | Topic | Where it lives |
        | --- | --- |
        | OOP | `Asher_Gbolahan/student.py` and `student_manager.py` |
        | File handling | `Grace_Ukpai_Akpu/data_handler.py` |
        | Regular expressions | `Great_Joseph/validate.py` |
        | Exception handling | `Ismail_Muhammed/` used by file, AI, and email calls |
        | GUI | This Streamlit shell plus the named UI folders |
        | Gemini AI | `Great_Joseph2/gemini_assistant.py` |
        | External API | Gmail SMTP in `Great_Joseph2/email_service.py` |
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Student Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="auto",
    )
    st.markdown(f"<style>{STYLES}</style>", unsafe_allow_html=True)
    require_access()

    with st.sidebar:
        st.markdown('<div class="brand"><span>✳</span> campus<span class="brand-dot">.</span></div>', unsafe_allow_html=True)
        st.caption("THE STUDENT WORKSPACE")
        page = st.radio("Navigate", PAGES, key="page", label_visibility="collapsed", format_func=lambda p: {"Dashboard":"◫   Overview", "Add Student":"＋   Enrol student", "View Students":"◎   Student directory", "Edit Student":"✎   Edit records", "Delete Student":"⊖   Remove student", "AI Assistant":"✦   Campus intelligence", "Email Reports":"↗   Send reports", "Team & Design":"◇   Meet the team"}[p])
        st.divider()
        st.caption("Your academic workspace. Manage students, track progress, and turn insights into action.")

    manager = _manager()

    if page == "Dashboard":
        render_dashboard(manager)
    elif page == "Add Student":
        _hero("Add Student", "Start a new student journey. Add their details below.", OWNERS[page])
        render_add_student(manager)
    elif page == "View Students":
        _hero("View Students", "Find the right student, explore results, and keep your class connected.", OWNERS[page])
        render_view_students(manager)
    elif page == "Edit Student":
        _hero("Edit Student", "Keep student details and academic results up to date.", OWNERS[page])
        render_edit_student(manager)
    elif page == "Delete Student":
        _hero("Delete Student", "Review the student details carefully before removing a record.", OWNERS[page])
        render_delete_student(manager)
    elif page == "AI Assistant":
        _hero("AI Assistant", "Ask plain-English questions about the class, or generate a one-paragraph student summary.", OWNERS[page])
        render_ai_assistant(manager)
    elif page == "Email Reports":
        _hero("Email Reports", "Share clear, personalised progress reports with your students.", OWNERS[page])
        render_email_report(manager)
    else:
        _hero("Team & Design", "Clear ownership, one folder per person, one working product.", OWNERS[page])
        render_team_page()


if __name__ == "__main__":
    main()
