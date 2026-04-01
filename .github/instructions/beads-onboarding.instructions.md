---
applyTo: ".beads/**,agents.md,.github/copilot-instructions.md,.github/skills/beads-workflow/SKILL.md"
description: "Use when onboarding a fresh clone, setting up Beads on a new machine, or syncing team issue state via bd backup fetch-git/export-git for local Dolt + Git backups."
---

# Beads Onboarding and Team Sync

Beads in this repository uses a local Dolt database and Git-based backup sync.

## Always-On Context Budget

For always-on compatibility files (`.github/copilot-instructions.md`, `agents.md`):

- Keep setup guidance to a short readiness gate only.
- Do not inline full installation and bootstrap playbooks.
- Route detailed setup and recovery steps to:
  - `.github/skills/environment-readiness/SKILL.md`
  - `.github/agents/development-environment-bootstrap.agent.md`
  - `.github/prompts/initialize-development-environment.prompt.md`

## Critical Model

- There is no Dolt remote server for team sync.
- Do not use `dolt pull` or `dolt push` for issue sharing.
- Do not configure Dolt remotes for normal team workflow.
- Share Beads state with:
  - `bd backup fetch-git` (restore latest team snapshot)
  - `bd backup export-git` (publish local snapshot)

## Tool Installation (Windows)

Install Beads and Dolt before first use.

Beads (PowerShell):

```powershell
irm https://raw.githubusercontent.com/steveyegge/beads/main/install.ps1 | iex
```

Reference releases:

- Beads: `https://github.com/gastownhall/beads/releases/tag/v0.63.3`
- Dolt: `https://github.com/dolthub/dolt/releases`

Expected install locations:

- `C:\Users\<user>\AppData\Local\Programs\bd\bd.exe`
- `C:\Users\<user>\AppData\Local\Programs\dolt\dolt.exe`

Required user PATH entries:

- `C:\Users\<user>\AppData\Local\Programs\bd`
- `C:\Users\<user>\AppData\Local\Programs\dolt`

If tools are already installed, setup should offer optional updates.

## Fresh Clone Setup

From repository root:

```bash
bd bootstrap
bd backup fetch-git
bd status
```

Then install/update hooks:

```bash
python install_hooks.py --force
```

## Session Start

```bash
git pull --rebase
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

Why realign `beads-backup`:

- `bd backup fetch-git` restores data but does not advance the local
  `beads-backup` branch pointer.
- If teammates exported since your last sync, export can fail non-fast-forward
  unless you realign first.

## During Work

- Claim before coding: `bd update <id> --claim --json`
- Publish claim for teammates: `bd backup export-git`
- Use `--description` with `bd create`
- Never use `bd edit` in automated workflows

## Session End

```bash
bd backup export-git
git push
```

If export fails non-fast-forward:

```bash
git branch -f beads-backup origin/beads-backup
bd backup export-git
```
