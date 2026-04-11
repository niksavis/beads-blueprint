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
7. Install managed git hooks (guard + Beads chaining)
8. Run quality verification
9. Commit setup-generated tracked files when present (`.gitignore`, `.beads/hooks/*`)
10. Require session kickoff prompt before any implementation work

Preflight requirement:

- Run setup as a no-intervention flow.
- `scripts/initialize_environment.py` must auto-select Python 3.14+, create `.venv`, and auto-install missing Python/Node tooling when platform package managers are available.
- If automatic install is impossible, stop and report exact blocker with the command/operator action needed.

Execution order:

1. Run:
   python scripts/initialize_environment.py
   If `python` is unavailable on Windows but `py` exists, run:
   py -3 scripts/initialize_environment.py
2. If Beads was not initialized by script, run:
   bd init --server --skip-agents --non-interactive
   If `--server` is unavailable in your installed `bd` version, run:
   bd init --skip-agents --non-interactive
3. Ensure hooks are current:
   python install_hooks.py --force
   python install_hooks.py --check
4. Verify toolchain:
   node --version
   npm --version
   python validate.py --fast
   python install_hooks.py --check
   dolt version
5. Commit setup-generated tracked files if they exist:
   - Run: `git status --short -- .gitignore .beads/hooks`
   - If output includes `.gitignore` or `.beads/hooks/*`, commit them in one setup commit.
   - Use a commit message that passes hook rules, for example:
     `chore(setup): record beads bootstrap artifacts (bd-setup)`
   - If git identity is missing, report exact local commands required and stop before commit.
6. Report PASS/FAIL for:
   - venv
   - dependencies
   - node tooling
   - Beads install
   - Dolt install
   - VS Code settings
   - git hooks
   - lint/static analysis
   - setup artifact commit status
7. If Windows PATH entries were added during setup, remind user to restart VS Code and open a new terminal.
8. Before any implementation, run `.github/prompts/start-work-session.prompt.md`.
   - If no actionable bead exists, create one with `--description`, claim it, publish it, and produce a short implementation plan.

Rules:

- Do not use shell-specific setup scripts.
- Keep everything cross-platform via Python commands.
- On Windows, if `python` command is unavailable but `py` exists, use `py -3` for Python script commands.
- If a step fails, show the command, exit code, and a minimal corrective action.
- Avoid prompting for user confirmations; prefer deterministic, non-interactive commands.
- Do not edit always-on policy files (`.github/copilot-instructions.md`, `agents.md`) during bootstrap.
- Never use `dolt pull` or `dolt push` in this repository; use `bd backup fetch-git` and `bd backup export-git`.
- Treat bootstrap as setup only: do not start implementation until session kickoff flow is complete.
