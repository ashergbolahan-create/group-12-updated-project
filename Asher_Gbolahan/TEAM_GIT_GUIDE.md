# Team repository guide

Team leader: **Asher Gbolahan**.

## What has been prepared

`main` contains the complete starting application. Each member has a branch matching their folder name. All branches start with the same complete project so everyone can run the app. These branches are workspaces for future changes; they do not claim separate historical contributions.

## Publish the shared repository

Asher creates an empty repository named `student-management-system` on the team's chosen Git host. Choose private unless the assignment requires public access. Do not initialize another README, license, or .gitignore: this project already has a starting commit.

After obtaining its actual repository URL, run these commands in this project folder, replacing REPOSITORY_URL:

```powershell
git remote add origin REPOSITORY_URL
git push -u origin main
git push origin Asher_Gbolahan Grace_Ukpai_Akpu Great_Joseph Oluwakorede_Olawoye Great_Joseph2 Ismail_Muhammed Grace_Ukpai_Akpu2
```

Asher invites each teammate through repository settings. Their GitHub usernames are needed for invitations. Where supported, protect main by requiring pull requests and review.

## Each teammate's workflow

Clone the shared repository once, then switch to your own branch. Example for Asher:

```powershell
git clone REPOSITORY_URL
cd student-management-system
git switch Asher_Gbolahan
```

Before making commits, configure your real name and email in your own clone:

```powershell
git config user.name "Your real name"
git config user.email "Your Git email or GitHub noreply address"
```

Edit your assigned files, run the app, then stage only the files you intend to submit. Example:

```powershell
git add Asher_Gbolahan
git commit -m "Describe the change you made"
git push -u origin Asher_Gbolahan
```

Open a pull request from your named branch into main. Asher reviews and merges agreed changes. Coordinate shared files such as app.py before editing them.

To bring approved work into your branch:

```powershell
git fetch origin
git merge origin/main
```

Do not force-push to solve conflicts. Review conflicting files with the team.

## Keys and records

Never commit .env or API keys. Every member creates their own local .env from .env.example. Inspect student records before publishing and use only approved demo data in a shared repository.

The starting commit uses the clearly labelled Project Setup identity, not a teammate's identity. Future work should be committed by its actual author. Named folders describe responsibility, not proof of authorship.
