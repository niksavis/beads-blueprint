# Beads Blueprint - Copilot Instructions

This is the canonical always-on policy for this template repository.

## Precedence

1. `.github/copilot-instructions.md` (this file)
2. `.github/instructions/*.instructions.md`
3. `.github/skills/**/SKILL.md`
4. `.github/prompts/*.prompt.md`

## Core Goals

- Keep this repository Python-first and cross-platform.
- Keep product/application code stack-agnostic; use Python for repository automation and setup.
- Use Beads as the primary issue tracker.
- Keep setup and quality gates simple, deterministic, and reproducible.

## Python Prerequisite Guidance

If `python` is unavailable during onboarding:

- Instruct user to install CPython from `python.org` before running setup.
- On Windows, prefer the full 64-bit installer and enable `Add python.exe to PATH`.
- Ask user to restart VS Code and open a new terminal session after install/PATH changes.
- Resume with: `python scripts/initialize_environment.py --yes-to-all`

## Initialization Policy

When user asks to initialize the repository, run:

1. `python scripts/initialize_environment.py --yes-to-all`
2. `bd --version`
3. `python validate.py --fast`
4. `python install_hooks.py --check`

If Beads has not been initialized yet:

- `bd init`
- `bd bootstrap`

## Terminal Policy

- Windows default: `Git Bash (.venv)`
- Linux/macOS default: `bash`
- PowerShell may be used as fallback only.

Never require shell-specific setup scripts in this template.

## Beads Workflow Rules

- Always include `--description` with `bd create`
- Never use `bd edit` in automated workflows
- Beads uses a local Dolt database; team sync is Git-based through backup commands.
- Do not use `dolt pull` or `dolt push` in this repository.
- Do not require or configure Dolt remotes for normal team sync.
- Start session sync sequence:
  1. `git pull --rebase`
  2. `bd backup fetch-git`
  3. `git branch -f beads-backup origin/beads-backup || true`
- Required lifecycle order:
  1. Claim: `bd update <id> --claim --json`
  2. Publish claim/state changes for teammates: `bd backup export-git`
  3. Implement + validate
  4. Close: `bd close <id> --reason "Done" --json`
  5. Commit with bead id in message
  6. Push code (`git push`)

## Quality Gate Rules

- Fast local gate: `python validate.py --fast`
- Commit gate: `python validate.py --commit`
- Full gate: `python validate.py --full`
- Hooks must be managed with:
  - `python install_hooks.py --force`
  - `python install_hooks.py --check`

## Dependency Management Rules

- Use package-file-first changes for dependencies.
- Do not perform ad-hoc installs without updating manifests/locks.
- Python dependency workflow:
  1. Update `requirements.in` or `requirements-dev.in`
  2. Refresh corresponding pinned lock files (`requirements.txt`, `requirements-dev.txt`)
  3. Use pip-tools to compile lockfiles from `.in` inputs
  4. Install dependencies from lockfiles, not from `.in` files
- Node/JavaScript workflow (if introduced in this repo):
  - Update `package.json` with fixed versions when practical.
  - Commit lockfiles (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`).
- Prefer fixed versions for reproducibility; if a range is required, document why.

## Release Rules

- Generate draft first:
  - `python regenerate_changelog.py --preview --json`
- Bump version with:
  - `python release.py patch|minor|major`
- Optional tagging:
  - `python release.py patch --tag`
- Keep changelog user-focused and concise

## Repository Hygiene

- No shell-specific setup scripts should be reintroduced.
- Prefer Python scripts for automation and initialization.
- Keep workflows lightweight and template-friendly.
