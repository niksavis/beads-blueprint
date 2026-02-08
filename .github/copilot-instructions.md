# Beads Template - Copilot Instructions

**See [agents.md](../agents.md) for complete workflow rules and conventions.**

## Project Initialization

When the user asks to "initialize the project", "setup the project", or similar, follow the **Project Initialization** section in [agents.md](../agents.md).

Key points:

- Check if already initialized (`.venv`, `tools/bin/bd*`, `.beads/issues.jsonl`)
- Warn and ask for confirmation if any components already exist
- Run the initialization sequence for the user's shell
- **CRITICAL**: Run team setup script (`setup_team.ps1` or `setup_team.sh`) after `bd init`
- Confirm completion and guide them to create a plan

**Team Setup Script** configures:

- Runs `bd doctor --fix` automatically
- Git remote and upstream tracking
- `beads-sync` branch for team collaboration
- Git hooks for Beads
- Initial sync to share issues with team

## Core Rules

1. Use any shell (PowerShell, bash, or Python scripts are all acceptable).
2. Do not assume terminal state persists between commands.
3. Activate the venv before any Python command.
4. No emoji in code, comments, or logs.
5. Do not include real customer data in commits or generated files.
6. Use Beads issue types: feature, task, subtask, bug.
7. Always include `--description` when creating Beads issues.
8. Never use `bd edit`.

## Venv Rule

PowerShell pattern:

```powershell
.venv\Scripts\activate; python scripts\plan_to_beads.py --help
```

bash pattern:

```bash
source .venv/bin/activate && python scripts/plan_to_beads.py --help
```

## Release Workflow

1. Generate or update changelog section:
   `python regenerate_changelog.py --version 0.1.1`
2. Bump version:
   `python release.py patch|minor|major`

## Beads Bootstrap

- Install and configure Beads using:
  - PowerShell: `& .\scripts\bootstrap_beads.ps1`
  - bash: `bash scripts/bootstrap_beads.sh`

- If Beads is already installed elsewhere, just configure the project:
  - PowerShell: `& .\scripts\configure_beads.ps1`
  - bash: `bash scripts/configure_beads.sh`

- **Execution Policy Issues**: If scripts are blocked, the bootstrap script will detect this and provide manual installation instructions. Never spawn a new PowerShell process with `powershell -ExecutionPolicy Bypass`, always run scripts in the current shell with `& .\script.ps1`

**Note**: Beads binary is extracted directly to `tools/bin/` (bd or bd.exe). This avoids
PATH length issues. Users add only `tools/bin` to PATH (once for all tools), or
invoke `tools/bin/bd` directly. Bootstrap scripts auto-detect existing Beads installations.

**VS Code Integration**: Bootstrap automatically creates `.vscode/settings.json` with workspace-specific
PATH configuration (`${workspaceFolder}\tools\bin`), enabling the VS Code Beads extension to find the
local daemon without affecting global settings.
