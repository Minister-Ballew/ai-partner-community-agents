"""
Regenerates index.json from every agents/<id>/agent.json on main, pinning
each to the current commit SHA. Runs in CI right after a merge to main, so
HEAD is exactly the approved commit. AI Partner reads only this pinned SHA
per agent — never a live branch — so an edit after approval can't silently
reach installed copies without going through review again.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"


def current_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> None:
    sha = current_sha()
    entries = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        agent_file = agent_dir / "agent.json"
        if not agent_dir.is_dir() or not agent_file.exists():
            continue
        agent = json.loads(agent_file.read_text(encoding="utf-8"))
        entries.append({
            "agent_id": agent_dir.name,
            "name": agent.get("name", ""),
            "description": agent.get("description", ""),
            "submitted_by_github": agent.get("submitted_by_github", ""),
            "commit_sha": sha,
        })

    (ROOT / "index.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote index.json with {len(entries)} agent(s) pinned to {sha}")


if __name__ == "__main__":
    main()
