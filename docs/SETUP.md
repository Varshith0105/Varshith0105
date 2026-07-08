# Setup Guide

This is a **GitHub Profile README** repo. To use it:

## 1. Create the special repository

Create a public repository on GitHub whose name **exactly matches your username**:

```
github.com/Varshith0105/Varshith0105
```

## 2. Push these files

```bash
git init
git add .
git commit -m "feat: cyber portfolio README"
git branch -M main
git remote add origin git@github.com:Varshith0105/Varshith0105.git
git push -u origin main
```

## 3. Enable the snake workflow

- Go to **Settings → Actions → General** and allow read/write permissions.
- Trigger `.github/workflows/snake.yml` once from the Actions tab.
- The snake SVGs are published on the `output` branch and consumed by the README via:
  `https://raw.githubusercontent.com/Varshith0105/Varshith0105/output/snake-dark.svg`

## 4. Assets

- `assets/svg/hero.svg` — hero banner (embeds your GitHub avatar via `https://github.com/Varshith0105.png`).
- `assets/svg/project-*.svg` — per-project illustration cards.
- All widgets (stats, streak, top languages, trophies) are pulled live from public services (`github-readme-stats`, `github-readme-streak-stats`, `github-profile-trophy`) — no build step required.

## 5. Customize

- Update project URLs and live-demo links inside `README.md`.
- Regenerate any SVG in `assets/svg/` if you change the color palette (Cyber Blue `#2ec5ff` → Purple `#c084fc`).
