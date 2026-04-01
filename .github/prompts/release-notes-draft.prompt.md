---
agent: 'agent'
model: GPT-5.3-Codex
tools: ['search/codebase', 'search', 'search/changes', 'execute/runInTerminal']
description: 'Draft concise user-focused release notes from repo changes'
---

Draft release notes for the current pending changes.

Rules:

- Use flat bullets focused on user benefit.
- Group related changes without over-detail.
- Do not include secrets, customer data, or internal-only noise.
- Keep language factual and concise.

Deliver:

- Suggested changelog bullets.
- Any follow-up checks before running release automation.
