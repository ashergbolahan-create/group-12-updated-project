"""Fresh-clone setup checks; never contact providers or use real credentials."""
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dotenv import dotenv_values
import setup_local
from Great_Joseph2 import setup_email
from Ismail_Muhammed.exceptions import EmailServiceError


class SetupTests(unittest.TestCase):
    def test_fresh_setup_and_rerun_preserve_private_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.env.example').write_text('GEMINI_API_KEY=\nAUTH_REQUIRED=false\n')
            with patch('setup_local.getpass', side_effect=['synthetic-key', '']), patch('builtins.input', return_value=''), patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(setup_local.main(root), 0)
                self.assertNotIn('synthetic-key', output.getvalue())
            with patch('setup_local.getpass', return_value=''), patch('builtins.input', return_value=''), patch('sys.stdout', new_callable=io.StringIO):
                setup_local.main(root)
            self.assertEqual(dotenv_values(root / '.env')['GEMINI_API_KEY'], 'synthetic-key')
            self.assertEqual(dotenv_values(root / '.env')['AUTH_REQUIRED'], 'false')

    @patch.dict(os.environ, {}, clear=True)
    def test_email_fresh_clone_prompts_and_defaults_recipient(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.env').write_text('TEST_EMAIL_RECIPIENT=\n')
            with patch.object(setup_email, 'ROOT', root), patch('builtins.input', return_value='sender@example.com'), patch.object(setup_email, 'getpass', return_value='abcdefghijklmnop'), patch.object(setup_email, 'send_test_email') as send, patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(setup_email.main(), 0)
            send.assert_called_once_with('sender@example.com')
            values = dotenv_values(root / '.env')
            self.assertEqual(values['GMAIL_ADDRESS'], 'sender@example.com')
            self.assertEqual(values['GMAIL_APP_PASSWORD'], 'abcdefghijklmnop')

    @patch.dict(os.environ, {}, clear=True)
    def test_rejected_email_does_not_save_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(setup_email, 'ROOT', root), patch('builtins.input', return_value='sender@example.com'), patch.object(setup_email, 'getpass', return_value='abcdefghijklmnop'), patch.object(setup_email, 'send_test_email', side_effect=EmailServiceError('Rejected')), patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(setup_email.main(), 1)
            self.assertFalse((root / '.env').exists())
