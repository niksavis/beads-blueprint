# Agent Instructions - Compatibility Shim

## Purpose

This file is a lightweight compatibility bootstrap for environments that do not
auto-load `.github/copilot-instructions.md`.

## Source of Truth

- Canonical policy: `.github/copilot-instructions.md`
- Conditional policy: `.github/instructions/*.instructions.md`
- Task workflows: `.github/skills/**/SKILL.md`

## Python Prerequisite Guidance

If `python` is unavailable during onboarding:

- Install CPython from `python.org` first.
- On Windows, prefer the full 64-bit installer and enable `Add python.exe to PATH`.
- Restart VS Code and open a new terminal session after install/PATH changes.
- Then run: `python scripts/initialize_environment.py --yes-to-all`

## Initialization Workflow

When asked to initialize the repository, run this sequence:

1. `python scripts/initialize_environment.py --yes-to-all`
2. `bd --version`
3. `python validate.py --fast`
4. `python install_hooks.py --check`

If Beads is not initialized yet, run:

- `bd init`
- `bd bootstrap`

## Beads + Dolt Sync Model (Critical)

Beads uses a local Dolt database in this repository.

- There is no Dolt remote server for team sync.
- Do not use `dolt pull` or `dolt push` for issue sharing.
- Do not configure Dolt remotes for this template workflow.
- Team sync is Git-based via `bd backup fetch-git` and `bd backup export-git`.

Session start:

```bash
git pull --rebase
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

Session end:

```bash
bd backup export-git
git push
```

If `bd backup export-git` fails with non-fast-forward, realign and retry:

```bash
git branch -f beads-backup origin/beads-backup
bd backup export-git
```

## Beads Rules

- Use `bd` for issue tracking.
- Always include `--description` when creating issues.
- Never use `bd edit` in agent workflows.
- Claim before work:
  - `bd update <id> --claim --json`
- Close before commit:
  - `bd close <id> --reason "Done" --json`

## Shell + Terminal Defaults

- Windows default terminal: `Git Bash (.venv)`
- Linux/macOS default terminal: `bash`
- PowerShell is fallback only

## Dependency Onboarding

For new Python dependencies:

1. Update `requirements.in` or `requirements-dev.in`
2. Regenerate corresponding `.txt` lock file with pip-tools
3. Re-run initialization or install explicitly in `.venv`

Install from lockfiles (`requirements.txt`, `requirements-dev.txt`), not from `.in` files.

For Node/JavaScript dependencies (if this repo adds a Node workspace):

1. Update `package.json` first
2. Use fixed versions when practical
3. Commit the corresponding lockfile (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`)

Do not use ad-hoc dependency installs that leave manifests/lockfiles unchanged.

## Session Completion

Before finishing implementation work:

1. `python validate.py --fast`
2. Ensure Beads lifecycle is complete for active work
3. Publish Beads snapshot before final push:
   - `bd backup export-git`
4. Verify hook state if changed:
   - `python install_hooks.py --check`
