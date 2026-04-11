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
- Keep always-on instructions minimal; route heavy workflows to on-demand skills/agents.

## Environment Readiness Gate

- Do not run full environment initialization by default.
- Run readiness checks only when setup status is unknown, user asks onboarding, or tool checks fail.
- Preflight checks:
  1. `python --version`
  2. `npm --version`
  3. `bd --version`
  4. `dolt version`
  5. `python install_hooks.py --check` (if Python is available)
- If checks pass, continue with requested task and skip setup flow.
- If checks fail, route to dedicated onboarding assets:
  - Skill: `.github/skills/environment-readiness/SKILL.md`
  - Agent: `.github/agents/development-environment-bootstrap.agent.md`
  - Prompt: `.github/prompts/initialize-development-environment.prompt.md`

For day-to-day development after setup:

- Session kickoff prompt: `.github/prompts/start-work-session.prompt.md`
- Greenfield kickoff prompt: `.github/prompts/greenfield-project-kickoff.prompt.md`

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
- Markdown quality checks require Node tooling from `npm ci`.
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
- Node/JavaScript workflow (required for repository markdown tooling):
  - Update `package.json` with fixed versions when practical.
  - Commit lockfiles (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`).
- Prefer fixed versions for reproducibility; if a range is required, document why.

## Release Rules

- Generate draft first:
  - `python regenerate_changelog.py --preview --json`
- Bump version with:
  - `python release.py patch|minor|major`
- Do not create or require git tags for template releases.
- Keep changelog user-focused and concise

## Repository Hygiene

- No shell-specific setup scripts should be reintroduced.
- Prefer Python scripts for automation and initialization.
- Keep workflows lightweight and template-friendly.
