---
agent: "Repo Quality Guardian"
description: "Run a strict self-review against template quality and safety rules before pushing"
---

This template usually works with trunk-based development. Perform a self-review
for the current working tree before pushing.

Checklist:

- Zero diagnostics in changed files (`get_errors`).
- Python-only automation policy remains intact.
- No emoji in code/logging/comments.
- No secrets or customer data introduced.
- Validation ran for changed behavior (`python validate.py --fast` minimum).
- Commit message readiness includes bead id trailer.
- Changes are minimal and avoid unrelated refactors.

Return:

- PASS/FAIL per checklist item
- File-level findings
- Concrete remediation steps for all FAIL items
