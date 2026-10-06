"""Run locally to enter a Gmail app password privately and send a test."""
from getpass import getpass
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv, set_key
from Great_Joseph2.email_service import send_test_email
from Ismail_Muhammed.exceptions import EmailServiceError
from Great_Joseph.validate import is_valid_email


def main():
    load_dotenv(ROOT / ".env", override=True)
    sender = os.getenv("GMAIL_ADDRESS", "")
    recipient = os.getenv("TEST_EMAIL_RECIPIENT", sender)
    if not is_valid_email(sender) or not is_valid_email(recipient):
        print("Set GMAIL_ADDRESS and TEST_EMAIL_RECIPIENT in .env first.")
        return 1
    print(f"Sender: {sender}\nTest recipient: {recipient}")
    print("Generate a Google app password at https://myaccount.google.com/apppasswords")
    print("This is NOT your regular Gmail password. Your input below is hidden.")
    password = getpass("Gmail app password: ").replace(" ", "").strip()
    if len(password) != 16 or not password.isascii() or not password.isalpha():
        print("Expected a 16-letter Google app password. Nothing was saved or sent.")
        return 1
    os.environ["GMAIL_APP_PASSWORD"] = password
    try:
        send_test_email(recipient)
    except EmailServiceError as exc:
        print(str(exc))
        return 1
    set_key(str(ROOT / ".env"), "GMAIL_APP_PASSWORD", password)
    print("Gmail accepted the test email. Check your inbox and spam folder.")
    print("The app password is saved in your local, Git-ignored .env file.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nSetup cancelled.")
