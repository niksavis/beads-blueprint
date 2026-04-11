---
applyTo: "**/*"
description: "Use when asked to review changes: prioritize correctness, regressions, security/data safety, and validation evidence with findings-first output."
---

# Review Instructions

Use this checklist when reviewing changes.

## Priority Order

1. Correctness and regressions
2. Security and data safety
3. Validation and test coverage
4. Maintainability and clarity

## Required Checks

- `get_errors` is clean for changed files.
- Python code has clear types and error handling.
- No secrets/customer data in code, docs, or logs.
- Setup automation remains Python-first and Node tooling requirements remain intact.
- Beads lifecycle steps are respected when bead ids are involved.
- Beads sync guidance uses `bd backup fetch-git` / `bd backup export-git` and does not rely on `dolt pull` / `dolt push` or `bd import` / `bd export`.
- Tests or validation gates were run, or skip reason is explicit.

## Review Output Format

- Findings first, ordered by severity.
- Include file references for each finding.
- Keep summary brief and secondary to findings.
