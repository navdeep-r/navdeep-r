# 🚀 GitHub Profile Setup Guide — Navdeep R

Complete instructions for pushing this profile to GitHub and activating all automation.

---

## Step 1 — Create the Special Profile Repository

1. Go to https://github.com/new
2. Set **Repository name** = `navdeep-r`  ← must match your GitHub username exactly
3. Set to **Public**
4. **Do NOT** initialise with a README (you'll push your own)
5. Click **Create repository**

---

## Step 2 — Push All Files

Open a terminal in this folder and run:

```bash
git init
git add .
git commit -m "feat: init GitHub profile README"
git branch -M main
git remote add origin https://github.com/navdeep-r/navdeep-r.git
git push -u origin main
```

---

## Step 3 — Activate GitHub Actions

Go to your new repo → **Settings** → **Actions** → **General**

Under *Workflow permissions*, select:
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

Click **Save**.

---

## Step 4 — Add Your Profile Photo (Optional — for ASCII Art)

1. Place your photo at `assets/source.jpg` (or `.png`) in the repo
2. Push it:
   ```bash
   git add assets/source.jpg
   git commit -m "chore: add source photo for ASCII art"
   git push
   ```
3. Manually trigger the workflow: **Actions** → **Generate ASCII Profile Art** → **Run workflow**

If no photo is added, a stylised `NR` placeholder is generated automatically.

---

## Step 5 — Trigger Snake Animation

Go to **Actions** → **Generate Snake Animation** → **Run workflow**

This generates `assets/github-snake-dark.svg` — a contribution grid snake animation.
To add it to your README, paste this inside any section:

```md
<div align="center">
  <img src="assets/github-snake-dark.svg" alt="snake"/>
</div>
```

---

## File Structure

```
navdeep-r/                         ← repo root (same as GitHub username)
├── README.md                      ← your profile page
├── SETUP.md                       ← this file
├── assets/
│   ├── source.jpg                 ← your photo (add manually)
│   ├── myself.png                 ← auto-generated ASCII art
│   ├── github-snake.svg           ← auto-generated snake (light)
│   └── github-snake-dark.svg      ← auto-generated snake (dark)
├── scripts/
│   ├── generate_ascii.py          ← ASCII art generator
│   └── requirements.txt
└── .github/
    └── workflows/
        ├── ascii-art.yml          ← weekly ASCII regeneration
        └── snake.yml              ← daily snake animation update
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Stats cards show "not found" | Your GitHub username must be `navdeep-r` exactly |
| Streak shows 0 | Give it 24h to sync after first push |
| ASCII art not generating | Check Actions → ascii-art workflow logs |
| Trophies not showing | Needs at least 1 public repo and some activity |

---

*Profile designed for GitHub username: **navdeep-r***
