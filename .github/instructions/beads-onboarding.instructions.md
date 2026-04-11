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

Upstream docs describe `bd dolt pull` / `bd dolt push` and Dolt-backed sync as
the default model.
This template intentionally uses Git-backed backup flow for team sync.

- There is no Dolt remote server for team sync.
- Do not use `dolt pull` or `dolt push` for issue sharing.
- Do not use `bd import` or `bd export` for team sync (migration/snapshot only).
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

Manual update workflow (Windows):

1. Download the latest release assets from the links above.
2. Use Windows zip assets and extract `bd.exe` / `dolt.exe` into:

- `C:\Users\<user>\AppData\Local\Programs\bd`
- `C:\Users\<user>\AppData\Local\Programs\dolt`

3. Verify tool versions:

- `bd --version`
- `dolt version`

If tools are already installed, setup should offer optional updates.

## Fresh Clone Setup

From repository root:

```bash
bd bootstrap
bd backup fetch-git
bd status
```

If `.beads/config.toml` exists (newer Beads docs), keep it tracked.
If `.beads/config.yaml` exists (older/newer compatibility behavior), keep it tracked.

Validate active issue prefix before work:

```bash
bd config list
```

Expected: prefix key/value exists and matches repository slug
(for example `my-project`).

Then install/update hooks:

```bash
python install_hooks.py --force
python install_hooks.py --check
```

If setup created or modified tracked bootstrap artifacts, commit them in one setup commit:

```bash
git status --short -- .gitignore .beads/hooks
```

Commit when changed:

```bash
git add .gitignore .beads/hooks
git commit -m "chore(setup): record beads bootstrap artifacts (bd-setup)"
```

## Session Start

Mandatory for every new session after Beads is initialized (`bd info --json` succeeds): run
`.github/prompts/start-work-session.prompt.md` before implementation.

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
- If no actionable bead exists, create one with `--description`, publish it, then claim it.
- Use `--description` with `bd create`
- Never use `bd edit` in automated workflows
- Add short implementation plan note before coding: `bd note <id> "Implementation plan: ..."`
- Commit trailers must use exact bead id, for example `(my-project-1234)`

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

## References

- https://gastownhall.github.io/beads/
- https://gastownhall.github.io/beads/cli-reference
- https://gastownhall.github.io/beads/reference/configuration
- https://gastownhall.github.io/beads/reference/git-integration
- https://gastownhall.github.io/beads/reference/faq
