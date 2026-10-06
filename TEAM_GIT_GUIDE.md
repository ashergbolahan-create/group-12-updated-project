# Team repository guide

Team leader: **Asher Gbolahan**.

Repository: https://github.com/ashergbolahan-create/group-12-updated-project

## Contributing

Each member works on their own branch and opens a pull request into `main`. Asher reviews and merges contributions. The shared app and supporting files are now integrated at the repository root.

Before starting new work, update your branch with the latest main:

```bash
git fetch origin
git merge origin/main
```

Stage only intended changes, commit with your own name and verified GitHub email, and push your branch. Do not force-push shared branches. Coordinate edits to app.py and other shared files with Asher.

## Run and test

```bash
py -3 -m pip install -r requirements.txt
py -3 -m streamlit run app.py
py -3 -B -m unittest discover -s tests -v
```

## Local configuration and records

Copy `.env.example` to `.env` locally for optional service credentials. Never commit `.env`, `.streamlit/secrets.toml`, API keys, passwords, Python caches, or agent configuration folders. Student records stay local; `data/students.example.csv` contains only the CSV header. The app creates the local CSV when records are saved.
