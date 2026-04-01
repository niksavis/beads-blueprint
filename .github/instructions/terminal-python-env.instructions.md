---
applyTo: "**/*.py,validate.py,install_hooks.py,release.py,regenerate_changelog.py,scripts/**/*.py"
description: "Use when running Python commands in terminals: enforce Git Bash-first Windows behavior, per-command venv activation, and cross-platform execution patterns."
---

# Terminal + Python Environment Instructions

Use shell and venv patterns that work across platforms.

## Shell Priority

- Windows: `Git Bash (.venv)` first, PowerShell fallback.
- Linux/macOS: `bash`.

## Venv Patterns

- Git Bash (Windows): `source .venv/Scripts/activate && <command>`
- PowerShell (Windows): `.venv\Scripts\Activate.ps1; <command>`
- Linux/macOS: `source .venv/bin/activate && <command>`

Or call interpreter directly:

- Windows: `.venv/Scripts/python.exe <args>`
- Linux/macOS: `.venv/bin/python <args>`

## Rules

- Do not assume terminal state persists between commands.
- Keep Python activation/interpreter selection in the same command invocation.
- Prefer `rg`/`fd` for search and discovery in bash-based shells.
- Use PowerShell cmdlets only as fallback on Windows.
