---
applyTo: "**/*.py"
description: "Use when editing Python files to enforce readability, typing, reliability, and cross-platform script behavior in this template."
---

# Python Code Quality Instructions

Apply these rules for Python changes.

## Core Rules

- Keep implementations clear and explicit.
- Use type hints on function inputs and outputs.
- Keep functions focused and easy to test.
- Handle edge cases intentionally (empty input, invalid values, missing files).

## Style

- Follow PEP 8.
- Use 4-space indentation.
- Use modern typing syntax (`list[str]`, `dict[str, str]`, `X | None`).
- Prefer context managers for files/subprocess resources.

## Imports

- Keep imports at file top-level.
- Order imports: stdlib, third-party, local.
- Avoid function-scoped imports unless there is a proven circular import case.

## Repository Constraints

- Setup/automation scripts must remain Python-only.
- Avoid shell-specific assumptions in script logic.
- Keep scripts cross-platform (Windows, Linux, macOS).

## Validation

1. Run `get_errors` for changed files.
2. Run `python validate.py --fast`.
3. If behavior changes, run relevant tests (or explicitly state why tests were skipped).
