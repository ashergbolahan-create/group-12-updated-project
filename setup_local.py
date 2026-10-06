"""Configure this computer without printing or uploading credentials."""
from getpass import getpass
from pathlib import Path

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parent


def main(root=ROOT):
    env = root / ".env"
    if not env.exists():
        # Exclusive creation protects an existing configuration.
        with env.open("x", encoding="utf-8") as target:
            target.write((root / ".env.example").read_text(encoding="utf-8"))
    values = dotenv_values(env)
    print("Settings are private to this computer. GitHub does not include them.")
    print("Press Enter to keep an existing value or skip an optional service.")
    print("Gemini keys: https://aistudio.google.com/apikey")
    print("OpenAI keys: https://platform.openai.com/api-keys")
    for name, label, secret in (
        ("GEMINI_API_KEY", "Gemini API key", True),
        ("OPENAI_API_KEY", "OpenAI API key", True),
        ("GMAIL_ADDRESS", "Gmail sender address", False),
    ):
        status = "configured" if values.get(name) else "not configured"
        prompt = f"{label} ({status}; Enter keeps it): "
        value = (getpass(prompt) if secret else input(prompt)).strip()
        if value:
            if name == "GMAIL_ADDRESS":
                from Great_Joseph.validate import is_valid_email
                if not is_valid_email(value):
                    print("Invalid email address; previous setting kept.")
                    continue
            set_key(str(env), name, value)
    print("Local settings saved. API keys have not been tested.")
    print("For email, run setup_email.bat to enter a Gmail app password and send a test.")
    print("Start or restart the app with run.bat. Local insights works without API keys.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nSetup stopped. Settings already saved remain in your local .env.")
        raise SystemExit(1)
