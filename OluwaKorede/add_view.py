"""Add Student and View All Students screens.

Owned by: Oluwakorede Olawoye  |  Branch: feature/add-view-ui
"""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from Asher_Gbolahan.student_manager import StudentManager
from Great_Joseph.validate import format_error_list, validate_student_fields
from Ismail_Muhammed.safe_action import safe_action


def render_dashboard(manager: StudentManager) -> None:
    students = manager.get_all()
    total = len(students)
    risk = len(manager.at_risk())
    average = manager.average_grade() or 0
    rate = round(100 * (total-risk)/total) if total else 0
    top = manager.top_student()
    st.markdown(f"""<div class="overview-head"><div><span class="eyebrow">YOUR CAMPUS, AT A GLANCE</span><h1>Big ambitions.<br><span class="heading-accent">Brighter futures.</span></h1><p>A little clarity. A lot of possibility. Meet your class today.</p></div><div class="orbit-art" aria-hidden="true"><div class="orbit o1"></div><div class="orbit o2"></div><div class="orbit o3"></div><div class="orbit-center">✳</div><span class="orbit-tag">THE NEXT CHAPTER ↗</span></div></div>
    <div class="editorial-grid"><div class="feature-card"><div class="card-top">01 / CLASS PULSE <span>↗</span></div><div class="big-number">{total:02d}<span>students.<br>limitless potential.</span></div><div class="feature-bottom"><span>Across {len(manager.courses())} courses</span><span>CONNECTED BY LEARNING</span></div></div><div class="score-card"><div class="card-top">02 / ATTAINMENT <span>✦</span></div><div class="score">{average:.1f}<small>/100</small></div><div class="score-track"><i style="width:{average}%"></i></div><p>Your class average</p></div><div class="support-card"><div class="card-top">03 / CHECK-IN <span>↗</span></div><div class="score">{risk:02d}</div><p>Students who could use<br>a little extra support.</p><span class="pill">Below the 50 pass mark</span></div></div>""", unsafe_allow_html=True)
    actions = st.columns(3)
    for col, label, destination in zip(actions, ['＋ Enrol a student', '↗ Explore the register', '✦ Ask your assistant'], ['Add Student','View Students','AI Assistant']):
        def navigate(target):
            st.session_state.page = target
        col.button(label, width="stretch", on_click=navigate, args=(destination,))
    if not students:
        st.info("Your next chapter starts with your first student. Use Enrol a student above.")
        return
    rows = ''
    for index, item in enumerate(sorted(students, key=lambda x: x.get_grade(), reverse=True)[:5],1):
        initials = ''.join(part[0] for part in item.get_name().split()[:2])
        rows += f'<div class="student-line"><span class="rank">{index:02d}</span><span class="avatar av{index%3}">{escape(initials)}</span><div class="student-info"><strong>{escape(item.get_name())}</strong><small>{escape(item.get_course())}</small></div><span class="student-grade">{item.get_grade():.0f}<small> / 100</small></span></div>'
    bars = ''
    for course in manager.courses():
        marks=[x.get_grade() for x in students if x.get_course()==course]
        value=sum(marks)/len(marks)
        bars += f'<div class="course-label"><span>{escape(course)}</span><strong>{value:.1f}</strong></div><div class="course-track"><i style="width:{value}%"></i></div>'
    st.markdown(f'<div class="lower-grid"><section class="white-card"><div class="section-title"><h3>Making their mark</h3><span>TOP 5 · BY GRADE</span></div>{rows}</section><section class="white-card"><div class="section-title"><h3>The bigger picture</h3><span>COURSES</span></div>{bars}<div class="standing-note"><span class="mini-ring" style="--rate:{rate}%">{rate}%</span><div><strong>Moving forward</strong><p>Students meeting the pass mark</p></div></div></section></div>', unsafe_allow_html=True)


def render_add_student(manager: StudentManager) -> None:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Enrol a student")
    st.caption("Fill in the student details. All fields are required.")

    with st.form("add_student_form", clear_on_submit=False):
        col_a, col_b = st.columns(2)
        with col_a:
            student_id = st.text_input("Student ID", placeholder="STU009")
            name = st.text_input("Full name", placeholder="Adaeze Okafor")
            email = st.text_input("Email", placeholder="adaeze.okafor@uni.edu.ng")
        with col_b:
            phone = st.text_input("Phone", placeholder="08031234567")
            course = st.text_input("Course", placeholder="Computer Science")
            grade = st.text_input("Grade (0–100)", placeholder="72")
        submitted = st.form_submit_button("Save student", width="stretch")

    if submitted:
        ok, errors = validate_student_fields(student_id, name, email, phone, course, grade)
        if not ok:
            for message in format_error_list(errors):
                st.error(message)
        else:
            success, _, error = safe_action(
                manager.add_student, student_id, name, email, phone, course, grade
            )
            if success:
                st.success(f"{name.strip()} ({student_id.strip()}) has been added to the register.")
                st.balloons()
            else:
                st.error(error)
    st.markdown("</div>", unsafe_allow_html=True)


def render_view_students(manager: StudentManager, compact: bool = False) -> None:
    students = manager.get_all()
    if not students:
        st.info("No students to display yet.")
        return

    if not compact:
        search_col, course_col, status_col = st.columns((2, 1.2, 1.2))
        query = search_col.text_input("Search name, ID or email")
        course = course_col.selectbox("Course", ["All courses"] + manager.courses())
        status = status_col.selectbox("Standing", ["Everyone", "In good standing", "At risk"])
        filtered = students
        needle = (query or "").strip().lower()
        if needle:
            filtered = [
                item
                for item in filtered
                if needle in item.get_name().lower()
                or needle in item.get_student_id().lower()
                or needle in item.get_email().lower()
            ]
        if course != "All courses":
            filtered = [item for item in filtered if item.get_course() == course]
        if status == "In good standing":
            filtered = [item for item in filtered if not item.is_failing()]
        elif status == "At risk":
            filtered = [item for item in filtered if item.is_failing()]
        st.caption(f"Showing {len(filtered)} of {len(students)} records.")
    else:
        filtered = students

    rows = []
    for item in filtered:
        rows.append(
            {
                "ID": item.get_student_id(),
                "Name": item.get_name(),
                "Course": item.get_course(),
                "Grade": item.get_grade(),
                "Letter": item.letter_grade(),
                "Standing": item.standing(),
                "Email": item.get_email(),
                "Phone": item.get_phone(),
            }
        )

    frame = pd.DataFrame(rows)
    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "Grade": st.column_config.ProgressColumn("Grade", min_value=0, max_value=100, format="%.1f"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
        },
    )
