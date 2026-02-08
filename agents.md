# Agent Instructions - Beads Template

## Purpose

Workflow rules and conventions for working with this Beads template.

## Project Initialization

When the user asks to "initialize the project", "setup the project", or similar:

1. **Check if already initialized:**
   - `.venv` directory exists → Python environment already setup
   - `tools/bin/bd.exe` or `tools/bin/bd` exists → Beads already installed locally
   - `.beads/issues.jsonl` exists → Beads already initialized
   - If ANY of these exist, warn the user and ask for confirmation before proceeding

2. **Initialization sequence (PowerShell):**

   ```powershell
   # Create Python environment
   python -m venv .venv
   .venv\Scripts\activate; pip install -r requirements.txt
   
   # Install Beads (runs in current shell)
   & .\scripts\bootstrap_beads.ps1
   
   # Add to PATH (session only)
   $env:Path += ";$PWD\tools\bin"
   
   # Initialize Beads
   bd init
   
   # Configure for team collaboration
   & .\scripts\setup_team.ps1
   ```

   **If execution policy blocks the script:**
   - Run: `& .\scripts\bootstrap_beads.ps1` directly in current shell
   - Or manually install: See [scripts/readme.md](scripts/readme.md) for manual installation steps
   - The script will provide clear instructions if it cannot run automatically

3. **Initialization sequence (bash):**

   ```bash
   # Create Python environment
   python -m venv .venv
   source .venv/bin/activate && pip install -r requirements.txt
   
   # Install Beads (no chmod needed)
   bash scripts/bootstrap_beads.sh
   
   # Add to PATH (session only)
   export PATH="$PWD/tools/bin:$PATH"
   
   # Initialize Beads
   bd init
   
   # Configure for team collaboration
   bash scripts/setup_team.sh
   ```

4. **Team Setup:** The `setup_team` script will:
   - Run `bd doctor --fix` to resolve common issues
   - Configure git remote (prompts if not set)
   - Create and push `beads-sync` branch for team collaboration
   - Set up git hooks and upstream tracking
   - Perform initial sync

5. **VS Code Integration:** The bootstrap script automatically creates `.vscode/settings.json` with workspace-specific PATH configuration, enabling the VS Code Beads extension to find the local daemon.

6. **Confirmation:** After successful initialization, inform the user they can now create a plan using `templates/plan_template.md`

## Platform and Tooling

- Any shell is acceptable (PowerShell, bash).
- Do not assume terminal state persists between commands.
- Activate the venv before any Python command.

## Python Virtual Environment

Activate the venv before any Python command:

```powershell
.venv\Scripts\activate; python scripts\plan_to_beads.py --help
```

```bash
source .venv/bin/activate && python scripts/plan_to_beads.py --help
```

## Team Collaboration Workflow

When working with a team, Beads uses a dedicated `beads-sync` branch to share issues:

**Before starting work (pull team changes):**

```powershell
git pull --rebase
bd sync --import
```

**Creating and updating issues:**

```powershell
bd create "Title" --description "Context" -p 2 -t feature --json
bd update <id> --status in_progress
bd close <id> --reason "Done"
```

**Sharing changes with team (push to beads-sync):**

```powershell
bd sync        # Exports to JSONL and commits to beads-sync
git push       # Shares with team
```

**Note:** The `setup_team` script handles the initial beads-sync branch creation and configuration. Team members should:

1. Clone the repository
2. Run bootstrap script to install Beads locally
3. Run setup_team script to configure their local environment
4. Use `bd sync --import` to pull team's issues

## Beads Basics

Use Beads issue types to keep work structured: `feature`, `task`, `subtask`, `bug`.
Always include a description.

```powershell
bd create "Title" --description "Context" -p 2 -t feature --json
bd create "Task" --description "Parent: Feature Title" -p 2 -t task --json
bd create "Subtask" --description "Parent: Task Title" -p 2 -t subtask --json
bd update <id> --status in_progress
bd close <id> --reason "Done"
```

## Plan to Beads

Use the plan template and the parser to generate Beads commands:

```powershell
Copy-Item -Force templates\plan_template.md plan.md
.venv\Scripts\activate; python scripts\plan_to_beads.py --plan plan.md --output beads_commands.ps1
& .\beads_commands.ps1
```

## Code Standards

- No emoji in code, comments, or logs.
- All Python functions should have type hints.

## Data Safety

- Do not include real customer data in commits or generated files.
- Use placeholders such as Acme Corp, example.com, customfield_10001.

## Required Workflow Rules

- Any shell is acceptable (PowerShell, bash).
- No emoji in code, comments, or logs.
- Use safe placeholders; do not include real customer data.
- Always include `--description` when creating Beads issues.
- Never use `bd edit`.

## Commit Rules

- Format: `type(scope): description (bd-XXX)`
- Close the bead before pushing.
