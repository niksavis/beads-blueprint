---
applyTo: "release.py,regenerate_changelog.py,changelog.md,version.py,readme.md"
description: "Use when drafting release notes, regenerating changelog previews, and bumping versions with release.py in no-tag template release workflows."
---

# Release Workflow Instructions

For release tasks:

- Generate changelog draft first:
  - `python regenerate_changelog.py --preview --json`
- Keep changelog entries concise and user-focused.
- Bump versions only through `release.py`.
- Do not create release tags for template workflows.

Checks:

1. Ensure no sensitive data appears in release notes.
2. Ensure version update touched only intended files.
3. Ensure release commands are platform-neutral Python invocations.
