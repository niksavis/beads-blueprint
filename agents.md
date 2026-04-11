# Agent Instructions - Compatibility Shim

## Purpose

This file is a lightweight compatibility bootstrap for environments that do not
auto-load `.github/copilot-instructions.md`.

## Source of Truth

- Canonical policy: `.github/copilot-instructions.md`
- Conditional policy: `.github/instructions/*.instructions.md`
- Task workflows: `.github/skills/**/SKILL.md`

## Always-On Context Budget

- Keep this shim minimal.
- Do not inline full onboarding/install playbooks here.
- Use readiness gate + routing so setup workflows load only when needed.

## Environment Readiness Gate

Run setup checks only when environment state is unknown or setup is requested.

Preflight checks:

```bash
python --version
py -3 --version   # Windows fallback when python alias is missing
npm --version
bd --version
dolt version
python install_hooks.py --check
py -3 install_hooks.py --check   # Windows fallback when python alias is missing
```

Decision:

- If checks pass, skip bootstrap and continue requested work.
- If checks fail, route to:
  - Skill: `.github/skills/environment-readiness/SKILL.md`
  - Agent: `.github/agents/development-environment-bootstrap.agent.md`
  - Prompt: `.github/prompts/initialize-development-environment.prompt.md`

## Beads + Dolt Sync Model (Critical)

Beads uses a local Dolt database in this repository.

- There is no Dolt remote server for team sync.
- Do not use `dolt pull` or `dolt push` for issue sharing.
- Do not use `bd import` or `bd export` for team sync (migration/snapshot only).
- Do not configure Dolt remotes for this template workflow.
- Team sync is Git-based via `bd backup fetch-git` and `bd backup export-git`.
- Code branch pushes/merges do not sync Beads state by themselves.

Session start:

```bash
git pull --rebase
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

For every new session after Beads is initialized (`bd info --json` succeeds),
run the session kickoff prompt before implementation work:

`.github/prompts/start-work-session.prompt.md`

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
- If no actionable bead exists, create one with `--description`, then publish and claim it.
- Close before commit:
  - `bd close <id> --reason "Done" --json`
- Commit messages must include exact bead id trailer, for example `(my-project-123)`.

## Session Completion

Before finishing implementation work:

1. `python validate.py --fast`
2. Ensure Beads lifecycle is complete for active work
3. Publish Beads snapshot before final push:
   - `bd backup export-git`
4. Verify hook state if changed:
   - `python install_hooks.py --check`
