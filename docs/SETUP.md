# Profile setup

## Workflows
| Workflow | Output | Needs |
|---|---|---|
| `metrics.yml` (lowlighter/metrics) | `metrics/metrics.classic.svg`, `metrics/metrics.isocalendar.svg` on `main` | `METRICS_TOKEN` secret |
| `snake.yml` | `github-snake-dark.svg` on `output` branch | nothing (GITHUB_TOKEN) |
| `profile-3d.yml` | `profile-3d-contrib/*.svg` | existing config |

## One-time: METRICS_TOKEN
1. GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)** → Generate new token.
2. Scopes: **`read:user`** and **`public_repo`** only (add `repo` only if you want private repos counted). Set an expiry you're comfortable with.
3. In this repo: Settings → Secrets and variables → Actions → **New repository secret** → name `METRICS_TOKEN`, paste the token.
4. Actions → **GitHub Metrics** → *Run workflow*. Check the run log; the two SVGs in `metrics/` replace the "generating…" placeholders.

The token is used only for reading your stats; commits use the built-in `GITHUB_TOKEN`. Never put the token in README or YAML.

## Editing
- Skills graphic: `assets/anim/skills-dark.svg` / `skills-light.svg` (pure SVG SMIL animation).
- Change the metrics schedule in `metrics.yml` (`cron`).
