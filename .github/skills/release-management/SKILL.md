---
name: release-management
description: "Use when preparing a release: generate changelog drafts, write concise release notes, bump semantic versions, and optionally create release tags."
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

4. Optionally create tag:

```bash
python release.py patch --tag
```

## Guardrails

- Do not add secrets/customer data to release notes.
- Keep release notes short and benefit-oriented.
- Preserve lightweight release behavior unless user requests otherwise.
