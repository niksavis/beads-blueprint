---
agent: "agent"
description: "Start a new work session: sync state, review open beads, claim next task, and confirm environment is ready before coding begins"
---

Start a new development session for this repository.

Steps:

1. Sync latest state:

   ```bash
   git pull --rebase
   bd backup fetch-git
   git branch -f beads-backup origin/beads-backup || true
   ```

2. Show open beads so the developer can pick work:

   ```bash
   bd ready --json
   ```

3. Confirm environment is ready:

   ```bash
   python --version
   npm --version
   bd --version
   python validate.py --fast
   python install_hooks.py --check
   ```

4. Ask the developer which bead to claim, then claim it:

   ```bash
   bd update <id> --claim --json
   bd backup export-git
   ```

Rules:

- Do not start any implementation until a bead is claimed and published.
- If `python validate.py --fast` fails, stop and report what is broken before proceeding.
- If `npm` is not found, install Node.js 20+, run `npm ci`, then rerun readiness checks.
- If `bd` or `dolt` are not found, route to `.github/agents/development-environment-bootstrap.agent.md`.
- Skip environment checks if the developer confirms the environment was already verified this session.
