"""
Regenerates index.json from every agents/<id>/agent.json on main, pinning
each to the current commit SHA. Runs in CI right after a merge to main, so
HEAD is exactly the approved commit. AI Partner reads only this pinned SHA
per agent — never a live branch — so an edit after approval can't silently
reach installed copies without going through review again.

Also ensures every agent has a companion GitHub issue used as its comment
thread and download counter: any authenticated GitHub user can comment on
or react to an issue on a public repo without needing push access to this
repo, so issue comments + reaction counts give us both features for free
without a custom database or counter file (which would need push access
this repo's other contributors don't have).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"
COMMENTS_MAP_FILE = ROOT / "moderation" / "comments_issues.json"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("REPO", "")
GITHUB_API = "https://api.github.com"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}


def current_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def load_comments_map() -> dict[str, int]:
    if not COMMENTS_MAP_FILE.exists():
        return {}
    try:
        return json.loads(COMMENTS_MAP_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def ensure_comments_issue(agent_id: str, name: str, comments_map: dict[str, int]) -> int | None:
    if agent_id in comments_map:
        return comments_map[agent_id]
    if not GITHUB_TOKEN or not REPO:
        return None  # local/manual run without CI context — skip issue creation
    r = requests.post(
        f"{GITHUB_API}/repos/{REPO}/issues",
        headers=HEADERS,
        json={
            "title": f"Comments: {name}",
            "body": (
                f"Discussion and feedback thread for the `{agent_id}` agent.\n\n"
                "React 👍 from AI Partner if you've imported this agent — that count is what "
                "shows as \"downloads\" in the app. Comment here with feedback or issues."
            ),
        },
        timeout=15,
    )
    r.raise_for_status()
    number = r.json()["number"]
    comments_map[agent_id] = number
    return number


def main() -> None:
    sha = current_sha()
    comments_map = load_comments_map()
    entries = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        agent_file = agent_dir / "agent.json"
        if not agent_dir.is_dir() or not agent_file.exists():
            continue
        agent = json.loads(agent_file.read_text(encoding="utf-8"))
        agent_id = agent_dir.name
        comments_issue = ensure_comments_issue(agent_id, agent.get("name", agent_id), comments_map)
        entries.append({
            "agent_id": agent_id,
            "name": agent.get("name", ""),
            "description": agent.get("description", ""),
            "submitted_by_github": agent.get("submitted_by_github", ""),
            "commit_sha": sha,
            "comments_issue": comments_issue,
        })

    (ROOT / "index.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    COMMENTS_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    COMMENTS_MAP_FILE.write_text(json.dumps(comments_map, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote index.json with {len(entries)} agent(s) pinned to {sha}")


if __name__ == "__main__":
    main()
