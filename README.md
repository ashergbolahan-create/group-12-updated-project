# Student Management System

A polished Streamlit registry for a five-person academic group project. Staff can add, view, edit and delete student records; every field is checked with regular expressions; every record is saved to a CSV file; failures never crash the app; Gemini can answer class questions; Gmail SMTP sends a grade report.

The work is split exactly as the proposal required: **one folder per teammate**.

---

## Run it

```bash
git clone https://github.com/ashergbolahan-create/group-12-updated-project.git
cd group-12-updated-project
py -3 -m pip install -r requirements.txt
py -3 -m streamlit run app.py
```

On Windows you can also double-click `run.bat`. Python 3.10 or newer is required.
`run.bat` starts the app without asking for optional credentials.
To enable live AI, run `setup_local.bat` separately to enter an API key, then
restart the app. Email sending requires `setup_email.bat` separately.

### Moving to another PC

GitHub contains the application, but intentionally excludes `.env` (passwords and
API keys) and `data/students.csv` (your student records). A new clone therefore
starts with an empty register and no live AI or email credentials.

1. Run `run.bat` to open the app. Optionally run `setup_local.bat` separately
   to enter a Gemini or OpenAI key if you want that provider.
2. Run `setup_email.bat` to enter your Gmail address and app password. This sends
   a test email to your own address unless `TEST_EMAIL_RECIPIENT` is set.
3. Restart the app. On the AI page, select the provider you configured, or choose
   **Local insights** to work without any API key.
4. To move existing records, close the app on both PCs and privately copy
   `data/students.csv` from the old PC into the new clone's `data` folder. Back up
   any existing destination CSV first; replacing it replaces that PC's register.

For another computer you personally control, you can also privately transfer your
existing `.env` into the project root instead of re-entering the settings. Do not
upload either private file to GitHub or share your credentials with teammates;
teammates should configure their own accounts. Clones do not sync student records.

The default server listens only on `127.0.0.1`, so this is a local application until shared sign-in is configured.

Optional keys go in a `.env` file (copy `.env.example`):

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Live Gemini answers and written summaries |
| `GMAIL_ADDRESS` | Sender for grade reports |
| `GMAIL_APP_PASSWORD` | Gmail **app password**, not the normal login |

Without those keys the rest of the system still runs. The AI page answers from the live register, and the email page still shows a full report preview.

---

## Who built what

| Member | Folder | Responsibility | Proposed branch |
| --- | --- | --- | --- |
| Asher Gbolahan | `Asher_Gbolahan/` | `Student` and `StudentManager` (OOP) | `Asher_Gbolahan` |
| Grace Ukpai Akpu | `Grace_Ukpai_Akpu/` | `save_to_file()` / `load_from_file()` | `Grace_Ukpai_Akpu` |
| Great Joseph | `Great_Joseph/` | Regex validation | `Great_Joseph` |
| Oluwakorede Olawoye | `Oluwakorede_Olawoye/` | Add Student, View Students, dashboard | `Oluwakorede_Olawoye` |
| Grace Ukpai Akpu | `Grace_Ukpai_Akpu2/` | Edit Student, Delete Student | `Grace_Ukpai_Akpu2` |
| Ismail Muhammed | `Ismail_Muhammed/` | Custom exceptions + `safe_action()` | `Ismail_Muhammed` |
| Great Joseph | `Great_Joseph2/` | Gemini, Gmail SMTP, this README | `Great_Joseph2` |

`app.py` is the shared shell. It only composes the folders above.

---

## Required topics

**OOP** — `Student` keeps fields private and exposes getters/setters, letter grades, and standing. `StudentManager` is the only class that adds, finds, edits, deletes, and asks the file layer to persist.

**File handling** — Python’s built-in `csv` module reads and writes `data/students.csv`. Every successful add, edit or delete rewrites the file immediately.

**Regular expressions** — `Great_Joseph/validate.py` checks student ID, name, email, phone, course and grade. Add and Edit both call the same functions.

**Exception handling** — File I/O, Gemini HTTP calls, and SMTP login/send all go through `safe_action()`. Expected problems raise `DuplicateStudentError`, `StudentNotFoundError`, `ValidationError`, `FileOperationError`, `AIServiceError` or `EmailServiceError`, and Streamlit shows a sentence instead of a traceback.

**GUI** — Streamlit sidebar navigation, dashboard metrics, searchable register, forms, confirmation on delete.

**Gemini AI** — Ask a class question or generate a one-paragraph student summary via the Gemini REST API.

**External API** — Grade reports are sent with Python’s built-in `smtplib` against `smtp.gmail.com`.

---

## Project layout

```
app.py
requirements.txt
data/students.csv
assets/styles.css
Asher_Gbolahan/
Grace_Ukpai_Akpu/
Great_Joseph/
Oluwakorede_Olawoye/
Grace_Ukpai_Akpu2/
Ismail_Muhammed/
Great_Joseph2/
```

---

## Git workflow (as proposed)

```bash
git checkout -b Asher_Gbolahan
git checkout -b Grace_Ukpai_Akpu
git checkout -b Great_Joseph
git checkout -b Oluwakorede_Olawoye
git checkout -b Grace_Ukpai_Akpu2
git checkout -b Ismail_Muhammed
git checkout -b Great_Joseph2
```

Merge into `main` through pull requests, one branch per person.

---

*Team lead: Asher Gbolahan. Built to match the group project proposal — GUI, OOP, file handling, exceptions, regex, Gemini, and an external email service.*


## Interface refresh and OpenAI assistant
The interface uses a bright blue and teal CampusHub theme. Team ownership folders are preserved.
Set `OPENAI_API_KEY` in the local, Git-ignored `.env` file and select OpenAI on the AI Assistant page.
`OPENAI_MODEL` defaults to `gpt-4.1-mini` and can be changed to a model available to your API project.
Never share the key in chat or commit `.env`. No key is bundled with the project.
The assistant sends academic context only when you submit a question or generate a summary.
Local insights remain available without credentials. Gemini remains selectable.
API documentation: https://developers.openai.com/api/docs/quickstart
CSV writes use atomic replacement and a file lock around each complete read/change/save transaction.
Failed add/edit/delete operations restore the saved in-memory state. Existing CSV rows are validated before use.


## GitHub repository

Repository: https://github.com/ashergbolahan-create/group-12-updated-project

The repository excludes local student records. The application creates data/students.csv when records are saved; data/students.example.csv documents the empty CSV format.

## Local fixes and email setup

All work can remain local: running the app, tests, or email setup does not commit or push anything.

- Independent saves reload the latest CSV under a cross-process lock so one user's addition does not erase another's.
- Edit forms retain the original record and reject changes if someone else updated it. Use **Reload current record** to review the latest version before trying again.
- Delete confirmation resets if the displayed record changes.
- Invalid CSV rows report their row number and validation problem. Correct the CSV while the app is closed, then retry.
- Local insights supports explicit whole-class questions such as `Who is below 80?` and `How many students are at least 50?`. Course-specific questions are directed to the directory filters instead of returning an unrelated answer.
- Gemini's model is configurable with `GEMINI_MODEL` in `.env`.

For Gmail, run `setup_email.bat`; it asks for the sender if it is not configured.
Optionally set `TEST_EMAIL_RECIPIENT` in `.env`; a blank value defaults to the sender.
Enable Google 2-Step Verification and create an app password at https://myaccount.google.com/apppasswords.
Then double-click `setup_email.bat`. It asks for the app password using hidden input, sends a test with no student data, and saves the password locally only after Gmail accepts the message.
Do not enter your normal Google password. If app passwords are unavailable for your account, consult https://support.google.com/accounts/answer/185833.
Restart the app after setup. The Email Reports page also has a test email button; student reports still go to each selected student's own address.

## Sign-in for shared access

Local-only mode is intended for a trusted user of this computer. It does not provide separate identities for people sharing the computer.
Do not expose local-only mode through a tunnel or reverse proxy.
For LAN or hosted access, the app refuses to show records until sign-in is enabled:

1. Register a Google OAuth web application. Set its authorized redirect URI to your app URL plus `/oauth2callback`.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. Supply the OAuth client ID, client secret, redirect URI and a random cookie secret (for example, generate one with `py -3 -c "import secrets; print(secrets.token_urlsafe(48))"`). Use HTTPS on a public deployment.
3. Set `AUTH_REQUIRED=true` and `ALLOWED_EMAILS=your-address@example.com` in `.env`. Multiple staff email addresses can be separated by commas. Every allowlisted staff member has full register access.
4. Only then change `server.address` for your intended network and restart. An unverified or non-allowlisted Google account cannot access the register.

The real Google login flow requires your OAuth account settings; automated tests use simulated identity claims and do not verify the live provider setup.

## Regression tests

Run `py -3 -B -m unittest discover -s tests -v` from this folder.
Tests use temporary records and mocked mail services; they do not modify your live CSV, send emails, or call AI providers.
