# AI Partner Community Agents

A shared, reviewed index of custom agents for [AI Partner](https://ballewster4.gumroad.com/l/vmgro). Anyone running AI Partner can submit an agent here from the Agent Builder's "Share to Community" action, and browse/import agents others have shared.

## How submission works

1. From AI Partner's Agent Builder, click "Share to Community" (requires connecting your GitHub account in Settings first). The app opens a pull request here on your behalf, adding `agents/<your-agent-id>/agent.json` and a `README.md`.
2. An automated check (`.github/workflows/screen.yml`) scans the submission for obviously malicious instructions (credential/file exfiltration, destructive commands, prompt-injection attempts) and posts the result as a PR comment.
3. A maintainer reviews and merges. Nothing is public until merged — the automated check narrows the review queue, it doesn't replace human judgment.
4. On merge, `index.json` is regenerated, pinning your agent to the exact commit SHA that was approved. AI Partner only ever reads that pinned SHA, never a live branch — so an agent can't be silently edited after approval without going through review again.

## Repo layout

```
agents/<agent-id>/agent.json   # {name, system_prompt, color, description, submitted_by_github}
agents/<agent-id>/README.md    # human-readable description
moderation/blocklist.json      # banned hardware IDs / GitHub usernames / emails, checked by AI Partner's license system
.github/workflows/             # screening + index-regeneration CI
scripts/                       # screening + index-build scripts used by CI
index.json                     # generated — do not hand-edit
```

## Safety note

An "agent" is a system prompt with tool access in the AI Partner app — the review process exists because a malicious prompt is the actual attack surface, not because of anything special about GitHub itself. Submitting a malicious agent may result in losing your AI Partner license and being blocked from future purchases.
