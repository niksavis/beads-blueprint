---
name: beads-workflow
description: "Use when onboarding to Beads, starting sessions, creating/claiming/closing issues, validating issue-prefix + commit trailer behavior, and applying this template's Git-backup sync model (bd backup fetch-git/export-git) while staying aligned with official bd CLI/reference guidance."
---

# Skill: Beads Workflow (Multi-Developer)

Use this skill to run Beads safely in this template while staying aligned with
official CLI/config references.

## Upstream vs Template Sync Model

Official docs describe `bd dolt pull` / `bd dolt push` and Dolt-backed sync
as the default model.
This template intentionally uses Git-backed Beads backups for team state sync:

- Session restore: `bd backup fetch-git`
- Session publish: `bd backup export-git`
- Code branch pushes/merges do not sync Beads state by themselves.
- Do not use `dolt pull` or `dolt push` in this template workflow.
- Do not use `bd import` or `bd export` for team sync in this template.

## Core Rules

- Always include `--description` when creating issues.
- Never use `bd edit`.
- For every new session after Beads is initialized (`bd info --json` succeeds), run
  `.github/prompts/start-work-session.prompt.md` before implementation.
- If `bd ready --json` has no actionable work, create a bead before coding.
- Claim issue before implementation; close issue before commit.
- Commit message trailer must use exact bead id, for example `(my-project-1234)`.

## Prerequisites

- `bd --version` succeeds.
- `bd info --json` succeeds.
- `bd hooks status` succeeds.
- Repository has run `bd bootstrap` at least once.
- On Windows, expected tool locations are:
  - `C:\Users\<user>\AppData\Local\Programs\bd\bd.exe`
  - `C:\Users\<user>\AppData\Local\Programs\dolt\dolt.exe`
- If upgrading manually on Windows, download release zip assets and extract
  `bd.exe` / `dolt.exe` into the same directories.

Quick verification:

```bash
bd --version
bd info --json
bd hooks status
bd status
```

If `bd info --json` fails in a fresh repository, initialize first and refresh hooks:

```bash
bd init --server --skip-agents --non-interactive || bd init --skip-agents --non-interactive
python install_hooks.py --force
python install_hooks.py --check
```

If setup changed tracked bootstrap artifacts, commit them:

```bash
git status --short -- .gitignore .beads/hooks
git add .gitignore .beads/hooks
git commit -m "chore(setup): record beads bootstrap artifacts (bd-setup)"
```

## Issue Prefix and Commit Trailer Sanity Check

Prefix must resolve to your project slug (for example `my-project`) so commit
trailers can be validated correctly.

```bash
bd config list
```

Expected outcome:

- A prefix key is present (`issue_prefix` on some builds, `id.prefix` on others)
- Prefix value matches repository slug (for example `my-project`)

Commit trailer rule:

- Use exact bead id returned by Beads, not free-form slug text
- Example: `feat(web): scaffold starter site (my-project-1234)`

## Step 0: Sync Before Starting Any Work

Always sync before creating or claiming a bead.

```bash
git pull --rebase
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

If you cannot pull code right now, use:

```bash
bd backup fetch-git
git branch -f beads-backup origin/beads-backup || true
bd ready --json
```

Why this matters:

- `bd backup fetch-git` restores Dolt data but does not move the local
  `beads-backup` branch pointer.
- If a teammate exported since your last session, export can fail with
  non-fast-forward until you realign that branch.

## Step 1: Search Before Creating

```bash
bd search "keyword" --json
bd list --status open --json
```

Decision rules:

- Exact duplicate: do not create a new bead.
- Related work exists: add note/dependency instead of duplicating.
- No match: proceed to creation.

## Step 2: Create the Bead

```bash
bd create "Short imperative title" \
  --description "Context and acceptance criteria" \
  -t feature|bug|task|chore \
  -p 0|1|2|3|4 \
  --json
```

Optional metadata from CLI reference:

- `--labels` / `-l`
- `--parent`
- `--deps` (for example `discovered-from:<id>`)

## Step 3: Export Immediately After Create

Publish new bead state so teammates can see it before coding starts.

```bash
bd backup export-git
```

## Step 4: Claim and Export Before Coding

```bash
bd update <id> --claim --json
bd backup export-git
```

Claim first, then export. This minimizes duplicate work windows.

Add lightweight execution plan note before coding:

```bash
bd note <id> "Implementation plan: 1) ... 2) ... 3) ..."
```

## Step 5: Mark Blocked If Needed

```bash
bd update <id> --status blocked --json
bd note <id> "Blocked by: <reason or dep-id>"
bd backup export-git
```

Optional dependency link:

```bash
bd dep add <id> <blocking-id>
bd dep tree <id>
bd dep cycles
```

Optional label/comment usage:

```bash
bd update <id> --add-label needs-review
bd comment add <id> "Implementation started"
```

## Step 6: Close and Push

```bash
bd close <id> --reason "Done" --json
git add .
git commit -m "type(scope): description (<exact-bead-id>)"
git push
```

If you close without pushing code in the same session, run:

```bash
bd backup export-git
```

## Troubleshooting

- `bd status` shows no issues after setup:
  - Run `bd backup fetch-git`.
- `bd backup export-git` fails non-fast-forward:
  - Run `git branch -f beads-backup origin/beads-backup` and retry.
- `bd backup export-git` fails due temp worktree cleanup on Windows:
  - Retry once; if second run says no changes to export, state is already published.
- Beads appears local-only for teammates:
  - Ensure export happened after create/claim/status changes.
- Sync/health anomalies persist:
  - Run `bd doctor`, then re-run session sync sequence.

## References

- https://gastownhall.github.io/beads/cli-reference
- https://gastownhall.github.io/beads/cli-reference/essential
- https://gastownhall.github.io/beads/cli-reference/issues
- https://gastownhall.github.io/beads/cli-reference/dependencies
- https://gastownhall.github.io/beads/cli-reference/labels
- https://gastownhall.github.io/beads/reference/configuration
- https://gastownhall.github.io/beads/reference/git-integration
- https://gastownhall.github.io/beads/reference/troubleshooting
