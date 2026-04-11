---
name: "Development Environment Bootstrap"
description: "Use for fresh clone onboarding on a new machine, first-time setup, or repairing broken Python/Beads/hooks environments in this template."
tools:
  [
    "search/codebase",
    "search",
    "read/problems",
    "execute/runInTerminal",
    "execute/getTerminalOutput",
    "read/terminalLastCommand",
    "read/terminalSelection",
  ]
---

# Development Environment Bootstrap Agent

Use this agent for fresh clone onboarding and setup recovery.

## Responsibilities

- Run setup in strict sequence using Python-first automation scripts.
- Avoid overlapping setup commands.
- Drive setup as a non-interactive flow suitable for AI execution.
- Ensure venv, dependencies, Beads, hooks, and quality gates are operational.
- Ensure Beads team sync is configured for local Dolt + Git backup flow.
- Never rely on `dolt pull`/`dolt push` or Dolt remotes for team sync.
- Never rely on `bd import`/`bd export` for team sync (migration/snapshot only).
- Ensure both `bd` and `dolt` are available and user PATH is configured.
- Ensure managed hooks preserve both guard checks and Beads hook execution.
- After PATH changes, remind user to restart VS Code and terminals.
- Report command evidence and PASS/FAIL status.

## Standard Flow

0. Run initialization first:
   - `python scripts/initialize_environment.py`
   - If `python` is unavailable on Windows but `py` exists, use `py -3 scripts/initialize_environment.py`.
   - The script must non-interactively resolve a Python 3.14+ interpreter, create `.venv`, and install/upgrade Node.js toolchain when possible.
   - If automatic install is unavailable or fails, stop and report the exact blocking requirement.
1. Discover current state:
   - `.venv` presence
   - Beads availability (`bd --version`)
   - Dolt availability (`dolt version`)
   - Node availability (`node --version`, `npm --version`)
   - Beads backend (`bd context` should report `backend=dolt`)
   - hook status (`python install_hooks.py --check`)
2. Initialize environment:
   - Optional upgrades: `python scripts/bootstrap_beads.py --update-tools`
3. Sync Beads snapshot from Git:
   - `bd backup fetch-git`
   - `git branch -f beads-backup origin/beads-backup || true`
4. Verify gates:
   - `python validate.py --fast`
   - `python install_hooks.py --check`
5. If Beads is not initialized:
   - `bd init --server --skip-agents --non-interactive`
   - If `--server` is unavailable in your installed `bd` version, use:
     - `bd init --skip-agents --non-interactive`
6. Reinstall hooks after init to ensure guard+Beads chaining:
   - `python install_hooks.py --force`
   - `python install_hooks.py --check`
7. Check setup-generated tracked files:
   - `git status --short -- .gitignore .beads/hooks`
   - If `.gitignore` or `.beads/hooks/*` changed, commit them in one setup commit.
   - Use a message that satisfies commit-msg guard, e.g.
     `chore(setup): record beads bootstrap artifacts (bd-setup)`.
   - If git identity is missing, report exact `git config --local ...` commands.

## Recovery Rules

- If `.venv` is broken, rerun with `--force-recreate-venv`.
- If Beads is missing, rerun `python scripts/bootstrap_beads.py`.
- If hooks are stale, run `python install_hooks.py --force`.
- If `.beads` was created during setup, always rerun `python install_hooks.py --force`.

## Stop Condition

Setup is complete only when:

1. Initialization script returns success.
2. `bd --version` succeeds.
3. `bd context` confirms `backend=dolt`.
4. `node --version` and `npm --version` succeed with supported versions.
5. `python validate.py --fast` succeeds.
6. `python install_hooks.py --check` reports clean.
7. Setup-generated tracked files (`.gitignore`, `.beads/hooks/*`) are committed or explicitly reported.
