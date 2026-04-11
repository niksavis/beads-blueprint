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
npm --version
bd --version
dolt version
python install_hooks.py --check
```

Optional quick quality probe after preflight:

```bash
python validate.py --fast
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
- `python --version` fails:
  - Instruct install of full 64-bit CPython from python.org.
  - On Windows, require `Add python.exe to PATH`.
  - Restart VS Code and open a new terminal, then rerun preflight.
- `npm --version` fails:
  - Instruct install of Node.js 20+.
  - Restart VS Code and open a new terminal, then rerun preflight.
- `bd` or `dolt` checks fail, or hooks fail:
  - Use agent `.github/agents/development-environment-bootstrap.agent.md`
  - Or run prompt `.github/prompts/initialize-development-environment.prompt.md`

## Guardrails

- Do not run full initialization by default on every task.
- Keep setup actions conditional and evidence-based.
- Keep all setup automation Python-first and cross-platform.
