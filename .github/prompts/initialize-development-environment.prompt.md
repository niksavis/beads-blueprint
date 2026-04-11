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

Initialize this repository for development using Python-first automation and required Node tooling for markdown checks.

Goals:

1. Create or refresh .venv
2. Install runtime and dev dependencies (linters, type checking, security tooling)
3. Install Node tooling for markdown quality checks (`npm ci`)
4. Bootstrap or verify Beads and Dolt with user-level install paths
5. Configure VS Code bash-first terminals (Git Bash (.venv) on Windows, bash on Linux/macOS)
6. Initialize Beads if not already initialized
7. Install managed git hooks
8. Run quality verification

Preflight requirement:

- Run setup as a no-intervention flow.
- `scripts/initialize_environment.py` must auto-select Python 3.14+, create `.venv`, and auto-install missing Python/Node tooling when platform package managers are available.
- If automatic install is impossible, stop and report exact blocker with the command/operator action needed.

Execution order:

1. Run:
   python scripts/initialize_environment.py
2. If Beads was not initialized by script, run:
   bd init --server --skip-agents --non-interactive
   If `--server` is unavailable in your installed `bd` version, run:
   bd init --skip-agents --non-interactive
   If Beads initialization updates `.gitignore` in a real project repository,
   commit that `.gitignore` change in the same setup commit.
3. Verify toolchain:
   node --version
   npm --version
   python validate.py --fast
   python install_hooks.py --check
   dolt version
4. Report PASS/FAIL for:
   - venv
   - dependencies
   - node tooling
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
- Avoid prompting for user confirmations; prefer deterministic, non-interactive commands.
