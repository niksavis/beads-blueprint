---
name: release-management
description: "Use when preparing a release: generate changelog drafts, write concise release notes, and bump semantic versions for no-tag template release workflows."
---

# Skill: Release Management

Use for release prep and versioning tasks.

## Workflow

1. Generate changelog draft:

```bash
python regenerate_changelog.py --preview --json
```

2. Update `changelog.md` with concise user-facing bullets.
3. Bump version:

```bash
python release.py patch|minor|major
```

## Guardrails

- Do not add secrets/customer data to release notes.
- Keep release notes short and benefit-oriented.
- Keep template releases tag-free unless the user explicitly changes policy.
