---
name: environment-readiness
description: "Use when development environment status is unknown, onboarding a fresh clone, or missing-tool errors suggest Python, npm, bd, dolt, hooks, or venv are not ready; run preflight checks and bootstrap only when checks fail."
---

# Skill: Environment Readiness

Use this skill to avoid unnecessary setup context and setup commands during normal coding work.

## When To Use

- User asks for first-time setup, onboarding, fresh clone, or new machine bootstrap.
- Commands fail with tool-not-found or environment-not-ready signals.
- You are unsure whether Python, npm, bd, dolt, hooks, or venv are configured.

## Preflight Checks

Run these checks in order:

```bash
python --version
py -3 --version   # Windows fallback when python alias is missing
npm --version
bd --version
dolt version
python install_hooks.py --check
py -3 install_hooks.py --check   # Windows fallback when python alias is missing
```

Optional quick quality probe after preflight:

```bash
python validate.py --fast
```

After any bootstrap/init run:

```bash
python install_hooks.py --force
python install_hooks.py --check
git status --short -- .gitignore .beads/hooks
```

If `.gitignore` or `.beads/hooks/*` changed, commit those files in one setup commit.
Use a commit message with bead-style trailer, for example:

```bash
git add .gitignore .beads/hooks
git commit -m "chore(setup): record beads bootstrap artifacts (bd-setup)"
```

## Windows Tool Paths (Beads + Dolt)

On Windows, expected install targets are:

- `C:\Users\<user>\AppData\Local\Programs\bd\bd.exe`
- `C:\Users\<user>\AppData\Local\Programs\dolt\dolt.exe`

Expected user PATH entries are:

- `C:\Users\<user>\AppData\Local\Programs\bd`
- `C:\Users\<user>\AppData\Local\Programs\dolt`

When updating tooling manually, use release assets and extract binaries directly
to those folders (Windows assets are zip files).

## Decision Gate

- All checks pass:
  - Skip bootstrap steps.
  - Continue directly with the requested coding task.
- `python --version` fails and `py -3 --version` also fails:
  - Instruct install of full 64-bit CPython from python.org.
  - On Windows, require `Add python.exe to PATH`.
  - Restart VS Code and open a new terminal, then rerun preflight.
- `npm --version` fails:
  - Instruct install of Node.js 20+.
  - Restart VS Code and open a new terminal, then rerun preflight.
- `bd` or `dolt` checks fail, or hooks fail:
  - Use agent `.github/agents/development-environment-bootstrap.agent.md`
  - Or run prompt `.github/prompts/initialize-development-environment.prompt.md`

## IDE Integration Readiness (Optional)

Use when user asks for editor/agent integration rather than base CLI setup.

CLI-native integrations (preferred when shell access exists):

```bash
bd setup claude --check
bd setup cursor --check
bd setup aider --check
```

GitHub Copilot MCP setup (optional, VS Code):

1. Install MCP server:

```bash
uv tool install beads-mcp
pip install beads-mcp
pipx install beads-mcp
```

2. Add project-level config file `.vscode/mcp.json`:

```json
{
  "servers": {
    "beads": {
      "command": "beads-mcp"
    }
  }
}
```

3. Optional: configure user-level VS Code MCP for all projects:

- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Linux: `~/.config/Code/User/mcp.json`
- Windows: `%APPDATA%\\Code\\User\\mcp.json`

4. Reload VS Code and verify Beads health:

```bash
bd version
bd doctor
bd hooks status
```

Notes:

- CLI + hooks usually has lower token overhead than MCP.
- MCP is useful when direct shell workflow is unavailable.

## Guardrails

- Do not run full initialization by default on every task.
- Keep setup actions conditional and evidence-based.
- Keep all setup automation Python-first and cross-platform.

## References

- https://gastownhall.github.io/beads/getting-started/ide-setup
- https://gastownhall.github.io/beads/cli-reference
- https://gastownhall.github.io/beads/reference/troubleshooting
