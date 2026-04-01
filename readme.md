# Beads Blueprint Template

Python-first template repository for teams using Beads as the issue tracker.

**Version:** 1.0.2

## What This Template Provides

- Python-only setup and automation scripts (no PowerShell or bash setup scripts)
- Stack-agnostic application development; Python is reserved for repository automation
- Beads + Dolt bootstrap with user-level installation and PATH checks
- Bash-first terminal defaults in VS Code:
  - Windows: `Git Bash (.venv)`
  - Linux/macOS: `bash`
- Development environment initialization in one command
- Lint/static-analysis toolchain and managed git hooks
- Copilot customization starter pack:
  - instructions
  - agents
  - skills
  - prompts
  - hook templates
- Lightweight release flow with changelog draft and version bumping
- Minimal GitHub Actions workflows for lint and build checks

## Prerequisites

- Python 3.13 or newer must be installed before running setup commands.
- If `python` is not available on Windows, install the full CPython installer from `python.org` (avoid Store-only installs for team consistency).
- During Windows Python install, enable `Add python.exe to PATH`.
- After installing Python, restart VS Code and open a new terminal session so PATH updates are applied.

## First-Time Setup (New Developer or AI Agent)

This repository is designed so a brand-new developer or AI agent can bootstrap
from a fresh clone on a new machine with no prior project knowledge.

### Recommended Bootstrap Path (Human or AI)

Run from repository root:

```bash
python scripts/initialize_environment.py --yes-to-all
```

Then verify setup:

```bash
bd --version
python validate.py --fast
python install_hooks.py --check
```

If `python` is missing on Windows, install full 64-bit CPython from
`python.org`, enable `Add python.exe to PATH`, restart VS Code, then rerun.

### AI Agent Entry Points

Use any of these entry points; they route to the same setup workflow:

- Agent: `.github/agents/development-environment-bootstrap.agent.md`
- Prompt: `.github/prompts/initialize-development-environment.prompt.md`
- Always-on policy: `.github/copilot-instructions.md` and `agents.md`
- Capability index: `.github/copilot_capability_map.md`

### Discovery-Friendly Task Phrases

These phrases are intentionally aligned with agent/skill/instruction
descriptions for stronger auto-discovery:

- "initialize this repo from scratch on a new machine"
- "bootstrap development environment and verify hooks"
- "set up Beads and team sync using backup fetch/export"
- "add dependency, regenerate lockfiles, and install from requirements txt"
- "run pre-push quality review and validation gates"

## Quick Start

### 1. Initialize Everything

Run from repository root:

```bash
python scripts/initialize_environment.py --yes-to-all
```

This command will:

1. Create or refresh `.venv`
2. Install runtime and dev dependencies
3. Install or verify Beads and Dolt
4. Configure VS Code terminal/task settings
5. Optionally run `bd init`
6. Install managed git hooks
7. Run `python validate.py --fast`

### 2. Verify Setup

```bash
bd --version
python validate.py --fast
python install_hooks.py --check
```

Optional tool upgrade (when `bd` and `dolt` already exist):

```bash
python scripts/bootstrap_beads.py --update-tools
```

If Beads or Dolt were installed for the first time and `bd`/`dolt` are still not found, restart VS Code and open a new terminal to reload PATH.

### 3. Team Sync (Shared Repository)

```bash
git pull --rebase
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

## Beads Workflow

### Core Lifecycle

1. Claim before work:

```bash
bd update <id> --claim --json
```

1. Implement and validate changes
1. Close bead before commit:

```bash
bd close <id> --reason "Done" --json
```

1. Commit with bead id in message

## Quality Gates

Quick gate:

```bash
python validate.py --fast
```

Commit gate:

```bash
python validate.py --commit
```

Full gate:

```bash
python validate.py --full
```

Install hooks:

```bash
python install_hooks.py --force
```

## Release Workflow

1. Generate changelog draft JSON:

```bash
python regenerate_changelog.py --preview --json
```

1. Draft release notes (manually or with prompt):

- `.github/prompts/release-notes-draft.prompt.md`

1. Bump version:

```bash
python release.py patch
python release.py minor
python release.py major
```

1. Template release flow does not create git tags.

## VS Code Defaults

Configured in `.vscode/settings.json`:

- Windows default terminal: `Git Bash (.venv)`
- Linux/macOS default terminal: `bash`

## GitHub Actions

- `.github/workflows/lint.yml`:
  - dependency install
  - `python validate.py --fast`
- `.github/workflows/build.yml`:
  - smoke build checks
  - changelog draft generation
  - optional tests if `tests/` exists

## Repository Layout

- `scripts/` - Python-only automation scripts
- `.github/instructions/` - conditional coding and workflow instructions
- `.github/skills/` - reusable workflows
- `.github/agents/` - specialized subagents
- `.github/prompts/` - reusable prompt templates
- `.github/hooks/` - hook configuration packs

## Dependency Management Policy

- Python dependencies:
  - Add runtime packages to `requirements.in`.
  - Add dev-only packages to `requirements-dev.in`.
  - Regenerate pinned lock files (`requirements.txt`, `requirements-dev.txt`) with `pip-compile`.
  - Install only from lock files (`requirements.txt`, `requirements-dev.txt`), never from `.in` files.
- Node/JavaScript dependencies (if a Node workspace is added later):
  - Add packages to `package.json` with fixed versions when possible.
  - Commit the corresponding lock file (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`).
- Avoid ad-hoc dependency installs that are not reflected in package/lock files.

## License

MIT. See `LICENSE`.
