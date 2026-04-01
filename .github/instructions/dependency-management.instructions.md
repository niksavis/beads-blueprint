---
applyTo: "**/*"
description: "Use when adding or updating dependencies: update requirements.in or requirements-dev.in, compile pinned lockfiles, and install from requirements.txt or requirements-dev.txt (never from .in files)."
---

# Dependency Management Instructions

Use these rules whenever dependencies are added or updated.

## Package-File-First Policy

- Do not run ad-hoc installs that leave manifests or lockfiles unchanged.
- Update dependency manifests first, then sync/install from those files.

## Python Rules

- Add runtime dependencies to `requirements.in`.
- Add dev dependencies to `requirements-dev.in`.
- Refresh corresponding lockfiles (`requirements.txt`, `requirements-dev.txt`) after updates.
- Regenerate lockfiles with pip-tools:
  - `python -m piptools compile requirements.in --output-file requirements.txt`
  - `python -m piptools compile requirements-dev.in --output-file requirements-dev.txt`
- Install dependencies from lockfiles (`requirements.txt`, `requirements-dev.txt`), not from `.in` files.
- Keep lockfiles pinned to exact versions for reproducibility.
- If exact pinning is not possible, explain why in task notes.

## Node/JavaScript Rules

- Add dependencies to `package.json` first.
- Prefer fixed versions when practical.
- Commit the corresponding lockfile (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`).
- Avoid `latest`-only additions in shared automation.

## Validation

1. Ensure manifest and lockfile changes are both present.
2. Ensure a clean-clone install is reproducible from committed files.
