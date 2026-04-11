---
agent: "Development Environment Bootstrap"
tools:
  [
    "search/codebase",
    "search",
    "search/changes",
    "execute/runInTerminal",
    "execute/getTerminalOutput",
    "read/problems",
  ]
description: "Initialize this repository from scratch with Python venv, Beads, hooks, lint/static-analysis tooling, and verification gates"
---

Initialize this repository for development using Python-only automation.

Goals:

1. Create or refresh .venv
2. Install runtime and dev dependencies (linters, type checking, security tooling)
3. Bootstrap or verify Beads and Dolt with user-level install paths
4. Configure VS Code bash-first terminals (Git Bash (.venv) on Windows, bash on Linux/macOS)
5. Initialize Beads if not already initialized
6. Install managed git hooks
7. Run quality verification

Preflight requirement:

- If `python` is not available, stop and provide install guidance.
- On Windows, direct user to full 64-bit CPython installer on `python.org`, ensure `Add python.exe to PATH` is enabled, then restart VS Code/new terminal.

Execution order:

1. Run:
   python scripts/initialize_environment.py --yes-to-all
2. If Beads was not initialized by script, run:
   bd init
3. Verify toolchain:
   python validate.py --fast
   python install_hooks.py --check
   dolt version
4. Report PASS/FAIL for:
   - venv
   - dependencies
   - Beads install
   - Dolt install
   - VS Code settings
   - git hooks
   - lint/static analysis
5. If Windows PATH entries were added during setup, remind user to restart VS Code and open a new terminal.

Rules:

- Do not use shell-specific setup scripts.
- Keep everything cross-platform via Python commands.
- If a step fails, show the command, exit code, and a minimal corrective action.
