"""Offline regression tests. Uses temporary CSVs; never sends email or calls AI."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Asher_Gbolahan.student_manager import StudentManager
from Asher_Gbolahan import access_control
from Great_Joseph2.gemini_assistant import _local_answer
from Great_Joseph2.email_service import send_test_email
from Ismail_Muhammed.exceptions import ConcurrentUpdateError, FileOperationError, DuplicateStudentError, EmailServiceError
from Ismail_Muhammed.safe_action import safe_action


def add(manager, sid="ZZ101", grade="70"):
    return manager.add_student(sid, "Test Student", "test@example.com", "08031234567", "Test Course", grade)


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "students.csv"
        self.manager = StudentManager(self.path)

    def test_two_stale_managers_preserve_both_additions(self):
        second = StudentManager(self.path)
        add(self.manager, "ZZ101")
        add(second, "ZZ102")
        self.assertEqual(StudentManager(self.path).count(), 2)

    def test_processes_preserve_all_additions(self):
        script = """import sys
from Asher_Gbolahan.student_manager import StudentManager
m = StudentManager(sys.argv[1])
for i in range(8):
 m.add_student('ZZ'+str(int(sys.argv[2])+i), 'Test Student', 'test@example.com', '08031234567', 'Test Course', '70')
"""
        jobs = [subprocess.Popen([sys.executable, "-B", "-c", script, str(self.path), str(base)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for base in (100, 200, 300)]
        for job in jobs:
            _, err = job.communicate(timeout=45)
            self.assertEqual(job.returncode, 0, err.decode())
        self.assertEqual(StudentManager(self.path).count(), 24)

    def test_duplicate_is_checked_against_disk(self):
        second = StudentManager(self.path)
        add(self.manager)
        with self.assertRaises(DuplicateStudentError):
            add(second)

    def test_stale_edit_and_delete_are_rejected(self):
        old = add(self.manager).to_dict()
        second = StudentManager(self.path)
        self.manager.edit_student("ZZ101", "Test Student", "test@example.com", "08031234567", "Test Course", "80")
        with self.assertRaises(ConcurrentUpdateError):
            second.edit_student("ZZ101", "Test Student", "test@example.com", "08031234567", "Test Course", "60", expected=old)
        with self.assertRaises(ConcurrentUpdateError):
            second.delete_student("ZZ101", expected=old)
        self.assertEqual(StudentManager(self.path).find_student("ZZ101").get_grade(), 80)

    def test_stale_public_save_is_rejected(self):
        second = StudentManager(self.path)
        add(self.manager)
        with self.assertRaises(ConcurrentUpdateError):
            second.save()
        self.assertEqual(StudentManager(self.path).count(), 1)

    def test_failed_save_restores_memory_and_disk(self):
        add(self.manager)
        before = self.path.read_bytes()
        with patch("Asher_Gbolahan.student_manager.save_to_file", side_effect=FileOperationError("Test write failure")):
            with self.assertRaises(FileOperationError):
                self.manager.edit_student("ZZ101", "Changed Name", "test@example.com", "08031234567", "Test Course", "80")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.manager.find_student("ZZ101").get_name(), "Test Student")

    def test_invalid_csv_reports_row_and_reason(self):
        for grade in ("999", "nan", "-1", "abc"):
            self.path.write_text("student_id,name,email,phone,course,grade\nZZ101,Test Student,test@example.com,08031234567,Test Course," + grade + "\n")
            ok, _, error = safe_action(StudentManager, self.path)
            self.assertFalse(ok)
            self.assertIn("Row 2", error)
            self.assertIn("Grade", error)

    def test_local_thresholds_and_scoped_questions(self):
        add(self.manager, "ZZ101", "40")
        add(self.manager, "ZZ102", "70")
        add(self.manager, "ZZ103", "80")
        self.assertTrue(_local_answer("Who is below 80?", self.manager).startswith("2 students below 80."))
        self.assertTrue(_local_answer("How many students are at least 80?", self.manager).startswith("1 students at least 80."))
        self.assertIn("whole-class", _local_answer("What is the average for Physics?", self.manager))


class EmailTests(unittest.TestCase):
    @patch.dict(os.environ, {"GMAIL_ADDRESS": "sender@example.com", "GMAIL_APP_PASSWORD": "fake password"})
    def test_test_email_is_addressed_correctly_without_student_data(self):
        with patch("Great_Joseph2.email_service.smtplib.SMTP_SSL") as smtp:
            send_test_email("recipient@example.com")
            message = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
            self.assertEqual(message["To"], "recipient@example.com")
            self.assertEqual(message["From"], "sender@example.com")
            self.assertIn("No student records", message.get_content())

    @patch.dict(os.environ, {"GMAIL_ADDRESS": "sender@example.com", "GMAIL_APP_PASSWORD": "fake password"})
    def test_network_failure_is_friendly(self):
        with patch("Great_Joseph2.email_service.smtplib.SMTP_SSL", side_effect=TimeoutError):
            with self.assertRaisesRegex(EmailServiceError, "connect securely"):
                send_test_email("recipient@example.com")


class AccessTests(unittest.TestCase):
    def test_nonlocal_access_without_login_is_blocked(self):
        with patch.dict(os.environ, {"AUTH_REQUIRED": "false"}), patch.object(access_control, "st") as st:
            st.get_option.return_value = "0.0.0.0"
            st.stop.side_effect = RuntimeError("stopped")
            with self.assertRaisesRegex(RuntimeError, "stopped"):
                access_control.require_access()
            st.error.assert_called_once()

    def test_oidc_requires_verified_allowlisted_email(self):
        for email, verified, allowed in [("owner@example.com", True, True), ("other@example.com", True, False), ("owner@example.com", False, False)]:
            with self.subTest(email=email, verified=verified), patch.dict(os.environ, {"AUTH_REQUIRED": "true", "ALLOWED_EMAILS": "owner@example.com"}), patch.object(access_control, "st") as st:
                st.secrets = {"auth": {key: "configured" for key in ("redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url")}}
                st.user.is_logged_in = True
                st.user.get.side_effect = {"email": email, "email_verified": verified}.get
                st.button.return_value = False
                st.stop.side_effect = RuntimeError("stopped")
                if allowed:
                    access_control.require_access()
                    st.stop.assert_not_called()
                else:
                    with self.assertRaises(RuntimeError):
                        access_control.require_access()


class AppTests(unittest.TestCase):
    def test_pages_crud_conflict_and_empty_states(self):
        from streamlit import config
        from streamlit.testing.v1 import AppTest
        config.set_option("server.address", "127.0.0.1")
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"AUTH_REQUIRED": "false", "OPENAI_API_KEY": "", "GEMINI_API_KEY": "", "GMAIL_APP_PASSWORD": ""}):
            copy = Path(temporary) / "app"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".env", ".agents", "tests", "__pycache__", "*.lock", "secrets.toml"))
            path = copy / "data/students.csv"
            path.write_text("student_id,name,email,phone,course,grade\n")
            add(StudentManager(path))
            app = AppTest.from_file(str(copy / "app.py"), default_timeout=15).run()
            pages = ["Dashboard", "Add Student", "View Students", "Edit Student", "Delete Student", "AI Assistant", "Email Reports", "Team & Design"]
            def button(label):
                return next(b for b in app.button if b.label == label)
            def page(name):
                app.radio[0].set_value(name).run()
                self.assertFalse(app.exception)
            for name in pages:
                page(name)
            page("Add Student")
            values = {"Student ID": "ZZ102", "Full name": "Test Second", "Email": "second@example.com", "Phone": "08031234567", "Course": "Test Course", "Grade (0–100)": "72"}
            for widget in app.text_input:
                widget.set_value(values[widget.label])
            button("Save student").click().run()
            self.assertTrue(app.success)
            button("Save student").click().run()
            self.assertTrue(app.error)
            page("View Students")
            app.text_input[0].set_value("ZZ102").run()
            self.assertEqual(len(app.dataframe[0].value), 1)
            page("Edit Student")
            app.selectbox[0].set_value("ZZ102 — Test Second").run()
            app.text_input(key="edit_ZZ102_grade").set_value("75")
            button("Save changes").click().run()
            self.assertTrue(app.success)
            self.assertEqual(StudentManager(path).find_student("ZZ102").get_grade(), 75)
            StudentManager(path).edit_student("ZZ102", "Test Second", "second@example.com", "08031234567", "Test Course", "80")
            app.text_input(key="edit_ZZ102_grade").set_value("60")
            button("Save changes").click().run()
            self.assertTrue(app.error)
            self.assertEqual(StudentManager(path).find_student("ZZ102").get_grade(), 80)
            button("Reload current record").click().run()
            self.assertEqual(app.text_input(key="edit_ZZ102_grade").value, "80.0")
            page("Delete Student")
            app.selectbox[0].set_value("ZZ102 — Test Second").run()
            self.assertTrue(button("Delete student").disabled)
            app.checkbox[0].check().run()
            button("Delete student").click().run()
            self.assertTrue(app.success)
            self.assertEqual(StudentManager(path).count(), 1)
            page("AI Assistant")
            app.selectbox[0].set_value("Local insights").run()
            app.chat_input[0].set_value("Who is below 80?").run()
            self.assertIn("1 students below 80", app.session_state["academic_chat"][-1]["content"])
            page("Email Reports")
            self.assertTrue(button("Send test email").disabled)
            self.assertTrue(button("Email report to student").disabled)
            StudentManager(path).delete_student("ZZ101")
            for name in pages:
                page(name)


if __name__ == "__main__":
    unittest.main()
