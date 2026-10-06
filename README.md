# Group 12 Updated Project

## Student Management System

Group 12 is building a Python and Streamlit application to manage student records. Planned features include adding, viewing, editing and deleting records, CSV storage, input validation, exception handling, an AI assistant and email reports.

**Group leader: Asher Gbolahan.**

## Starting point

This README is the shared starting file. Each member will create their own branch and submit their assigned folder themselves. The full application will be assembled after the contributions have been reviewed and merged.

## Responsibilities

- **Asher Gbolahan:** `Asher_Gbolahan/` — Student and StudentManager classes; integration and review coordination.
- **Grace Ukpai Akpu:** `Grace_Ukpai_Akpu/` — CSV file handling; `Grace_Ukpai_Akpu2/` — edit and delete screens.
- **Great Joseph:** `Great_Joseph/` — regular expression validation; `Great_Joseph2/` — AI and email integrations.
- **Oluwakorede Olawoye:** `Oluwakorede_Olawoye/` — add and view screens and dashboard.
- **Ismail Muhammed:** `Ismail_Muhammed/` — custom exceptions and safe action handling.

Folder spelling and capitalization must match the shared imports exactly. Two assigned folders for the same person can be submitted on that person's branch.

## How to contribute

1. Clone this repository, or update your existing clone from `main`.
2. Create your own branch from the latest `main`. If your named branch already exists, coordinate with Asher before reusing it.
3. Add only your assigned folder or folders. Do not upload another member's work.
4. Commit with a clear message and push your branch.
5. Open a pull request into `main`. Asher reviews and merges accepted work.

Example for a new Asher branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c Asher_Gbolahan
git add Asher_Gbolahan/
git commit -m "Add student model and manager"
git push -u origin Asher_Gbolahan
```

Use your own name for your branch and stage only your assigned files. Do not force-push shared branches.

## Shared integration files

Asher will coordinate the shared `app.py`, `requirements.txt`, application settings and assets as the modules are merged. The existing full app imports members' modules, so it should only be added when those dependencies are available. This starter does not yet run the complete application.

## Keep private files out of Git

Never commit `.env`, API keys, passwords, `.streamlit/secrets.toml`, Python cache files or real student records. Use placeholder configuration and approved demonstration data only.
