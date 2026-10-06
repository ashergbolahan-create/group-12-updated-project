"""Broader functional checks using synthetic records and mocked external services."""
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Asher_Gbolahan.student_manager import StudentManager
from Great_Joseph.validate import validate_student_fields
from Great_Joseph2.email_service import send_grade_report
from Great_Joseph2.openai_service import post_openai
from Great_Joseph2.gemini_assistant import _post_gemini
from Ismail_Muhammed.exceptions import AIServiceError


class ExtendedTests(unittest.TestCase):
    def test_validation_and_grade_boundaries(self):
        fields = dict(student_id='ZZ101', name='Test Student', email='test@example.com',
                      phone='08031234567', course='Test Course', grade='70')
        for field, invalid in [('student_id','!'), ('name','123'), ('email','bad'),
                               ('phone','12'), ('course','!'), ('grade','101'),
                               ('grade','nan'), ('grade','-1')]:
            with self.subTest(field=field, invalid=invalid):
                valid, errors = validate_student_fields(**dict(fields, **{field:invalid}))
                self.assertFalse(valid)
                self.assertIn(field, errors)
        with tempfile.TemporaryDirectory() as folder:
            m = StudentManager(Path(folder)/'students.csv')
            for i, (grade, letter) in enumerate([(0,'F'),(39.9,'F'),(40,'E'),(45,'D'),(50,'C'),(60,'B'),(70,'A'),(100,'A')]):
                student=m.add_student(**dict(fields,student_id=f'ZZ{100+i}',grade=str(grade)))
                self.assertEqual(student.letter_grade(),letter)
                self.assertEqual(student.is_failing(),grade<50)
            self.assertEqual(StudentManager(Path(folder)/'students.csv').count(),8)

    @patch.dict(os.environ, {'OPENAI_API_KEY':'fake','GEMINI_API_KEY':'fake'})
    def test_ai_success_and_errors(self):
        fixtures=[(post_openai, {'output':[{'content':[{'type':'output_text','text':'Synthetic response'}]}]}),
                  (_post_gemini, {'candidates':[{'content':{'parts':[{'text':'Synthetic response'}]}}]})]
        for function, body in fixtures:
            with self.subTest(provider=function.__name__):
                with patch('urllib.request.urlopen') as request:
                    request.return_value.__enter__.return_value=io.BytesIO(json.dumps(body).encode())
                    self.assertEqual(function('Synthetic test'), 'Synthetic response')
                for failure in [TimeoutError(), urllib.error.URLError('offline')]:
                    with patch('urllib.request.urlopen',side_effect=failure):
                        with self.assertRaises(AIServiceError): function('Synthetic test')
                for body in [b'not json', b'{}', b'{"candidates":[{"content":{"parts":[{"text":""}]}}]}']:
                    with patch('urllib.request.urlopen') as request:
                        request.return_value.__enter__.return_value=io.BytesIO(body)
                        with self.assertRaises(AIServiceError): function('Synthetic test')

    @patch.dict(os.environ, {'GMAIL_ADDRESS':'sender@example.com','GMAIL_APP_PASSWORD':'fake'})
    def test_report_delivery_payload(self):
        with tempfile.TemporaryDirectory() as folder:
            m=StudentManager(Path(folder)/'students.csv')
            student=m.add_student('ZZ101','Test Student','test@example.com','08031234567','Test Course','49')
            with patch('Great_Joseph2.email_service.smtplib.SMTP_SSL') as smtp:
                send_grade_report(student)
                message=smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
                self.assertEqual(message['To'],'test@example.com')
                self.assertIn('49.0 (D)',message.get_content())
                self.assertIn('At risk',message.get_content())

    def test_filters_navigation_validation_and_ai_fallback(self):
        from streamlit import config
        from streamlit.testing.v1 import AppTest
        config.set_option('server.address','127.0.0.1')
        env={'AUTH_REQUIRED':'false','OPENAI_API_KEY':'fake','GEMINI_API_KEY':'fake',
             'GMAIL_ADDRESS':'sender@example.com','GMAIL_APP_PASSWORD':'fake'}
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,env):
            copy=Path(temporary)/'app'
            shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','.env','.agents','tests','__pycache__','*.lock','secrets.toml'))
            path=copy/'data/students.csv'
            path.write_text('student_id,name,email,phone,course,grade\n')
            m=StudentManager(path)
            m.add_student('ZZ101','First Student','first@example.com','08031234567','Physics','40')
            m.add_student('ZZ102','Second Student','second@example.com','08031234567','Chemistry','80')
            app=AppTest.from_file(str(copy/'app.py'),default_timeout=15).run()
            def button(label): return next(b for b in app.button if b.label==label)
            def page(name):
                app.radio[0].set_value(name).run()
                self.assertFalse(app.exception)
            for label,dest in [('＋ Enrol a student','Add Student'),('↗ Explore the register','View Students'),('✦ Ask your assistant','AI Assistant')]:
                page('Dashboard'); button(label).click().run()
                self.assertEqual(app.radio[0].value,dest)
                self.assertFalse(app.exception)
            page('Add Student'); button('Save student').click().run()
            self.assertEqual(len(app.error),6)
            self.assertEqual(StudentManager(path).count(),2)
            page('View Students')
            app.selectbox[0].set_value('Physics').run()
            self.assertEqual(list(app.dataframe[0].value['ID']),['ZZ101'])
            app.selectbox[0].set_value('All courses').run()
            app.selectbox[1].set_value('In good standing').run()
            self.assertEqual(list(app.dataframe[0].value['ID']),['ZZ102'])
            app.text_input[0].set_value('no matching record').run()
            self.assertEqual(len(app.dataframe[0].value),0)
            self.assertFalse(app.exception)
            page('Delete Student'); app.checkbox[0].check().run()
            m.edit_student('ZZ101','First Student','first@example.com','08031234567','Physics','60')
            app.run()
            self.assertTrue(button('Delete student').disabled)
            page('AI Assistant')
            for provider,target in [('OpenAI','Great_Joseph2.openai_service.post_openai'),('Gemini','Great_Joseph2.gemini_assistant._post_gemini')]:
                app.selectbox[0].set_value(provider).run()
                with patch(target,side_effect=AIServiceError('Synthetic outage')):
                    app.chat_input[0].set_value('What is the class average?').run()
                    self.assertTrue(app.warning)
                    self.assertIn('70.0',app.session_state['academic_chat'][-1]['content'])
                    button('Generate summary').click().run()
                    self.assertTrue(app.warning)
                    self.assertFalse(app.exception)
            button('Clear conversation').click().run()
            self.assertEqual(app.session_state['academic_chat'],[])
            page('Email Reports')
            with patch('Great_Joseph2.email_service.smtplib.SMTP_SSL') as smtp:
                button('Email report to student').click().run()
                self.assertTrue(app.success)
                smtp.return_value.__enter__.return_value.send_message.assert_called_once()


if __name__=='__main__': unittest.main()
