import json
import os
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from xml.sax.saxutils import escape

USER = os.environ.get("GITHUB_USERNAME", "Varshith0105")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"

def get_json(path):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def txt(x, y, value, size=14, color="#E5E7EB", weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" font-family="Segoe UI,Arial,sans-serif">{escape(str(value))}</text>'

def rect(x, y, w, h, fill="#151923", stroke="#343B49", rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'

repos = get_json(f"/users/{USER}/repos?per_page=100&sort=updated")
events = get_json(f"/users/{USER}/events/public?per_page=100")
stars = sum(repo.get("stargazers_count", 0) for repo in repos)
forks = sum(repo.get("forks_count", 0) for repo in repos)
open_issues = sum(repo.get("open_issues_count", 0) - repo.get("open_prs_count", 0) for repo in [])
# Repository list API's open_issues_count includes issues and PRs; use issue search for accurate public issue count.
try:
    open_issue_search = get_json(f"/search/issues?q=type:issue+state:open+author:{USER}&per_page=1")
    open_issue_count = open_issue_search.get("total_count", 0)
except Exception:
    open_issue_count = sum(max(0, repo.get("open_issues_count", 0)) for repo in repos)
try:
    open_pr_search = get_json(f"/search/issues?q=type:pr+state:open+author:{USER}&per_page=1")
    open_pr_count = open_pr_search.get("total_count", 0)
except Exception:
    open_pr_count = sum(1 for event in events if event.get("type") == "PullRequestEvent" and event.get("payload", {}).get("action") == "opened")

months = []
now = datetime.now(timezone.utc)
for i in range(5, -1, -1):
    month = (now.month - 1 - i) % 12 + 1
    year = now.year + ((now.month - 1 - i) // 12)
    months.append((year, month))
labels = [datetime(y, m, 1).strftime("%b") for y, m in months]
activity = defaultdict(lambda: {"push": 0, "pr": 0, "issues": 0})
repo_activity = Counter()
for event in events:
    try:
        dt = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
    except Exception:
        continue
    key = (dt.year, dt.month)
    typ = event.get("type")
    if typ == "PushEvent":
        activity[key]["push"] += max(1, len(event.get("payload", {}).get("commits", [])))
        repo_activity[event.get("repo", {}).get("name", "").split("/")[-1]] += max(1, len(event.get("payload", {}).get("commits", [])))
    elif typ == "PullRequestEvent":
        activity[key]["pr"] += 1
    elif typ == "IssuesEvent":
        activity[key]["issues"] += 1

W, H = 1100, 650
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg.append('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#10131B"/><stop offset="1" stop-color="#191323"/></linearGradient><linearGradient id="pink" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#DB2777"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs>')
svg.append('<rect width="1100" height="650" rx="14" fill="url(#bg)"/>')
svg.append(txt(28, 38, f"{USER}  /  GITHUB ACTIVITY DASHBOARD", 21, "#F9FAFB", 700))
svg.append(txt(28, 62, "Public profile metrics • refreshed automatically by GitHub Actions", 12, "#9CA3AF"))
svg.append(txt(1070, 38, now.strftime("UPDATED %d %b %Y"), 10, "#F472B6", 700))

metrics = [
    ("PUBLIC REPOSITORIES", len(repos), "#22D3EE"),
    ("STARS EARNED", stars, "#FBBF24"),
    ("OPEN ISSUES", open_issue_count, "#F472B6"),
    ("OPEN PULL REQUESTS", open_pr_count, "#A78BFA"),
]
for i, (label, value, accent) in enumerate(metrics):
    x = 25 + i * 267
    svg.append(rect(x, 82, 250, 105))
    svg.append(txt(x+16, 109, label, 11, "#9CA3AF", 700))
    svg.append(txt(x+16, 151, value, 32, "#FFFFFF", 700))
    svg.append(f'<rect x="{x+16}" y="169" width="218" height="4" rx="2" fill="{accent}" opacity=".9"/>')

# Monthly activity area chart from public GitHub events (GitHub API exposes a limited recent history).
svg.append(rect(25, 205, 650, 280))
svg.append(txt(45, 234, "RECENT PUBLIC ACTIVITY", 14, "#F3F4F6", 700))
svg.append(txt(45, 254, "Pushes / commits, pull requests and issue events from recent public events", 10, "#9CA3AF"))
chart_x, chart_y, chart_w, chart_h = 65, 282, 570, 150
max_val = max([activity[(y,m)][k] for y,m in months for k in ("push","pr","issues")] + [1])
for j in range(4):
    gy = chart_y + j * chart_h / 3
    svg.append(f'<line x1="{chart_x}" y1="{gy:.1f}" x2="{chart_x+chart_w}" y2="{gy:.1f}" stroke="#374151" stroke-width="1"/>')
for idx, (y,m) in enumerate(months):
    cx = chart_x + idx * (chart_w / max(1, len(months)-1))
    svg.append(txt(cx-12, chart_y+chart_h+22, labels[idx], 10, "#9CA3AF"))
for key, color in (("push","#F472B6"),("pr","#A78BFA"),("issues","#FBBF24")):
    pts = []
    for idx, (y,m) in enumerate(months):
        val = activity[(y,m)][key]
        px = chart_x + idx * (chart_w / max(1, len(months)-1))
        py = chart_y + chart_h - (val / max_val) * (chart_h-12)
        pts.append((px, py))
    svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    for x,y in pts:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')
svg.append(f'<circle cx="75" cy="463" r="4" fill="#F472B6"/>{txt(85,467,"Pushes / commits",10,"#D1D5DB")}')
svg.append(f'<circle cx="220" cy="463" r="4" fill="#A78BFA"/>{txt(230,467,"Pull requests",10,"#D1D5DB")}')
svg.append(f'<circle cx="350" cy="463" r="4" fill="#FBBF24"/>{txt(360,467,"Issue events",10,"#D1D5DB")}')

# Most active repositories from recent push events.
svg.append(rect(695, 205, 380, 280))
svg.append(txt(715, 234, "RECENTLY ACTIVE REPOSITORIES", 14, "#F3F4F6", 700))
top_repos = repo_activity.most_common(5)
if not top_repos:
    svg.append(txt(715, 275, "No recent public push events found.", 12, "#9CA3AF"))
else:
    max_repo = max(v for _,v in top_repos) or 1
    for idx, (name, count) in enumerate(top_repos):
        yy = 275 + idx * 37
        svg.append(txt(715, yy, name[:32], 11, "#E5E7EB", 600))
        svg.append(rect(715, yy+8, 260, 8, "#272333", "#272333", 4))
        svg.append(f'<rect x="715" y="{yy+8}" width="{max(4,260*count/max_repo):.1f}" height="8" rx="4" fill="url(#pink)" stroke="none"/>')
        svg.append(txt(990, yy+5, count, 10, "#F9A8D4", 700))

# Top repositories by stars.
svg.append(rect(25, 505, 1050, 118))
svg.append(txt(45, 532, "TOP STARRED PUBLIC REPOSITORIES", 14, "#F3F4F6", 700))
top_starred = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:4]
for idx, repo in enumerate(top_starred):
    x = 45 + idx * 255
    name = repo.get("name", "")[:28]
    svg.append(txt(x, 561, name, 11, "#F9A8D4", 600))
    svg.append(txt(x, 585, f"★ {repo.get('stargazers_count', 0)}   •   Forks {repo.get('forks_count', 0)}", 10, "#D1D5DB"))
    svg.append(txt(x, 605, f"Language: {repo.get('language') or 'Not specified'}"[:35], 10, "#9CA3AF"))
svg.append(txt(28, 640, "Activity chart reflects recent public events only; GitHub API does not expose full private activity here.", 10, "#9CA3AF"))
svg.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/github-activity-dashboard.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
