"""Email a student's grade report through Gmail SMTP.

Owned by: Great Joseph  |  Branch: feature/ai-email-integration
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st

from Asher_Gbolahan.student import Student
from Asher_Gbolahan.student_manager import StudentManager
from Ismail_Muhammed.exceptions import EmailServiceError
from Ismail_Muhammed.safe_action import safe_action
from Great_Joseph.validate import is_valid_email


def build_report(student: Student) -> str:
    return (
        f"Dear {student.get_name()},\n\n"
        "This is your current grade report from the Student Management System.\n\n"
        f"Student ID : {student.get_student_id()}\n"
        f"Course     : {student.get_course()}\n"
        f"Grade      : {student.get_grade()} ({student.letter_grade()})\n"
        f"Standing   : {student.standing()}\n"
        f"Pass mark  : {Student.PASS_MARK}\n\n"
        "If you have questions about this result, please contact your course tutor.\n\n"
        "Kind regards,\n"
        "Academic Registry\n"
        "Student Management System\n"
    )


def _send_email(recipient: str, subject: str, body: str) -> None:
    sender = (os.getenv("GMAIL_ADDRESS") or "").strip()
    password = (os.getenv("GMAIL_APP_PASSWORD") or "").strip().replace(" ", "")
    if not sender or not password:
        raise EmailServiceError(
            "Gmail is not configured. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to your .env file."
        )

    if not is_valid_email(sender) or not is_valid_email(recipient):
        raise EmailServiceError("Enter a valid sender and recipient email address.")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=25, context=ssl.create_default_context()) as smtp:
            smtp.login(sender, password)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        raise EmailServiceError(
            "Gmail rejected the login. Use a Gmail App Password, not your ordinary account password."
        ) from exc
    except smtplib.SMTPException as exc:
        raise EmailServiceError("The email server could not send this report.") from exc
    except OSError as exc:
        raise EmailServiceError("Could not connect securely to Gmail. Check your internet connection and try again.") from exc


def send_grade_report(student: Student) -> None:
    _send_email(student.get_email(),
                f"Grade report — {student.get_name()} ({student.get_student_id()})",
                build_report(student))


def send_test_email(recipient: str) -> None:
    """Verify delivery without including any student information."""
    _send_email(recipient, "Student Management System — email test",
                "This is a test email from your Student Management System.\n"
                "Your Gmail email setup is working. No student records are included.\n")


def render_email_report(manager: StudentManager) -> None:
    configured = bool(
        (os.getenv("GMAIL_ADDRESS") or "").strip() and (os.getenv("GMAIL_APP_PASSWORD") or "").strip()
    )
    if configured:
        st.caption(f"Sender: {os.getenv('GMAIL_ADDRESS')} · Credentials entered; delivery is verified only after sending.")
    else:
        st.info(
            "Email sending needs GMAIL_ADDRESS and GMAIL_APP_PASSWORD in `.env`. "
            "You can still preview the report below."
        )
        st.caption("Run setup_email.bat to enter your Gmail app password privately and send a test email.")
        st.link_button("Google app-password instructions", "https://support.google.com/accounts/answer/185833")

    recipient = st.text_input("Test email recipient", value=os.getenv("TEST_EMAIL_RECIPIENT", ""))
    if st.button("Send test email", disabled=not configured):
        ok, _, error = safe_action(send_test_email, recipient)
        if ok:
            st.success(f"Test email accepted by Gmail for {recipient}. Check the inbox and spam folder.")
        else:
            st.error(error)

    students = manager.get_all()
    if not students:
        st.info("Add a student before sending a grade report.")
        return

    labels = {f"{item.get_student_id()} — {item.get_name()}": item for item in students}
    picked = st.selectbox("Student", list(labels.keys()), key="email_picker")
    student = labels[picked]

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Report preview")
    st.code(build_report(student), language="text")
    st.caption(f"Recipient: {student.get_email()}")
    if st.button("Email report to student", type="primary", width="stretch", disabled=not configured):
        ok, _, error = safe_action(send_grade_report, student)
        if ok:
            st.success(f"Grade report sent to {student.get_email()}.")
        else:
            st.error(error)
    st.markdown("</div>", unsafe_allow_html=True)
