---
name: beads-workflow
description: "Use when onboarding to Beads, starting work, creating or claiming beads, publishing claim/state changes, syncing with bd backup fetch-git/export-git, closing work, and pushing code in multi-developer local Dolt + Git backup workflows."
---

# Skill: Beads Workflow (Multi-Developer)

Use this skill to keep Beads state consistent across teammates when Beads is backed
by a local Dolt database and synchronized through Git backups.

## Core Rules

- Always include `--description` when creating issues.
- Never use `bd edit`.
- Claim issue before implementation.
- Close issue before commit.
- Team sync is Git-based via `bd backup fetch-git` and `bd backup export-git`.
- Do not use `dolt pull` or `dolt push` for Beads issue sharing.

## Prerequisites

- `bd --version` succeeds.
- `bd context` shows `backend=dolt`.
- Repository has run `bd bootstrap` at least once.

Quick verification:

```bash
bd --version
bd context
bd status
```

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

## Step 5: Mark Blocked If Needed

```bash
bd update <id> --status blocked --json
bd note <id> "Blocked by: <reason or dep-id>"
bd backup export-git
```

Optional dependency link:

```bash
bd dep add <id> <blocking-id>
```

## Step 6: Close and Push

```bash
bd close <id> --reason "Done" --json
git add .
git commit -m "type(scope): description (bd-<id>)"
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
