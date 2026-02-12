# Beads Template - Copilot Instructions

**See [agents.md](../agents.md) for complete workflow rules and conventions.**

## Project Initialization

When the user asks to "initialize the project", "setup the project", or similar, follow the **Project Initialization** section in [agents.md](../agents.md).

Key points:

- Check if already initialized (`.venv`, `tools/bin/bd*`, `.beads/issues.jsonl`)
- Warn and ask for confirmation if any components already exist
- Verify Python is installed; if missing, stop and guide the user to https://www.python.org/downloads/
- Narrate each major step (venv creation, Beads install, VS Code setup, `bd init`, team setup)
- Run the initialization sequence for the user's shell
- **CRITICAL**: Run team setup script (`setup_team.ps1` or `setup_team.sh`) after `bd init`
- Confirm completion and guide them to create a plan

Post-initialization workflow:

- Ask the user for their first feature
- Create a plan file in `plans/` based on `templates/plan_template.md`
- Ask if the plan is ready to create Beads from it
- If yes, convert the plan to JSONL, import into Beads, and ask which Bead to start first

**Team Setup Script** configures:

- Runs `bd doctor --fix` automatically
- Git remote and upstream tracking
- **Synchronizes with remote repository** (handles divergent histories automatically)
- `beads-sync` branch for team collaboration
- Git hooks for Beads
- Initial sync to share issues with team

**Remote Synchronization:**

- If the remote repository was initialized with files (README, LICENSE, etc.), the script automatically merges using `--allow-unrelated-histories`
- If merge conflicts occur, the script will exit with clear instructions to resolve them manually
- After resolving conflicts, simply re-run the setup_team script

**Push Safety:**

- Before any push to remote, users are shown what will be pushed and asked to confirm (y/n)
- Use `-YesToAll` (PowerShell) or `--yes-to-all` (bash) to skip confirmations for automated workflows
- Each push operation clearly displays the repository URL and branch name before proceeding
- If no commits exist and the working tree has files, the script prompts to create an initial commit

## Core Rules

1. Use any shell (PowerShell, bash, or Python scripts are all acceptable).
2. Do not assume terminal state persists between commands.
3. Activate the venv before any Python command.
4. No emoji in code, comments, or logs.
5. Do not include real customer data in commits or generated files.
6. Use Beads issue types: epic, feature, task, bug, chore, merge-request, molecule (most common: feature, task, bug, epic, chore).
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

**Recommended (LLM-assisted changelog):**

1. Generate changelog draft:

   ```powershell
   .venv\Scripts\activate; python regenerate_changelog.py --preview --json
   ```

   Creates `changelog_draft.json` with commits since last tag.

2. Ask Agent/LLM to write changelog:
   - "Read changelog_draft.json and write a polished changelog section for v0.1.1"
   - Agent generates user-friendly Features/Bug Fixes/Improvements sections
   - Copy agent's output to `changelog.md` as `## v0.1.1` section (prepend it)

3. Bump version:

   ```powershell
   .venv\Scripts\activate; python release.py patch|minor|major
   ```

   Updates `version.py` and `readme.md` automatically.

4. Commit and tag:
   ```powershell
   git add . && git commit -m "Release v0.1.1"
   git tag v0.1.1 && git push origin main --tags
   ```

**Alternative (manual TBD placeholders):**

1. Bump version (creates TBD placeholders):

   ```powershell
   python release.py patch|minor|major
   ```

2. Edit `changelog.md` manually to replace TBD sections

3. Commit and tag as above

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

## Plan to Beads Workflow

Convert structured plans into Beads issues automatically using JSONL import.

**Quick Start:**

1. Create plan from template:

   ```powershell
   New-Item -ItemType Directory -Force -Path plans
   Copy-Item templates\plan_template.md plans\my-feature.md
   ```

2. Edit `plans\my-feature.md` with your features and tasks

3. Convert to JSONL:

   ```powershell
   .venv\Scripts\activate; python scripts\plan_to_beads.py --plan plans\my-feature.md --output plan_issues.jsonl
   ```

4. Import into Beads:

   ```powershell
   Get-Content plan_issues.jsonl | Add-Content .beads\issues.jsonl
   bd sync --import
   Remove-Item plan_issues.jsonl
   ```

5. Verify:
   ```powershell
   bd list
   ```

**Plan Template Format:**

- `### Feature: Title [P1]` - Feature with priority (P1-P3)
- `- Task: Title [P2]` - Task under feature (P1-P3)
- `- Notes: Context` - Additional context for features or tasks

**Benefits of JSONL approach:**

- Batch import is much faster than individual commands
- No shell escaping issues
- Native Beads format
- Can create multiple plans and import iteratively

**See [agents.md](../agents.md) for detailed workflow and examples.**
