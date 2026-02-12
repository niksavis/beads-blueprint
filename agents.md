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

2. **Verify Python is installed:**
   - If `python` is not available, stop and guide the user to install Python from <https://www.python.org/downloads/>
   - On Windows, remind the user to check “Add Python to PATH” during installation

3. **Narrate background steps:**
   - Before each major step (venv creation, Beads install, VS Code setup, `bd init`, team setup), explain what will happen and why

4. **Initialization sequence (PowerShell):**

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
   
   # Start daemon if not already running (first-time setup)
   # Subsequent VS Code opens will auto-start via tasks.json
   if (-not (bd daemon status 2>$null)) { bd daemon start --auto-commit --auto-push }
   
   # Optional: configure for team collaboration (creates/pushes beads-sync)
   & .\scripts\setup_team.ps1
   ```

   **If execution policy blocks the script:**
   - Run: `& .\scripts\bootstrap_beads.ps1` directly in current shell
   - Or manually install: See [scripts/readme.md](scripts/readme.md) for manual installation steps
   - The script will provide clear instructions if it cannot run automatically

   **To skip push confirmations (for automation):**

   ```powershell
   & .\scripts\setup_team.ps1 -YesToAll
   ```

5. **Initialization sequence (bash):**

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
   
   # Start daemon if not already running (first-time setup)
   # Subsequent VS Code opens will auto-start via tasks.json
   bd daemon status 2>/dev/null || bd daemon start --auto-commit --auto-push
   
   # Optional: configure for team collaboration (creates/pushes beads-sync)
   bash scripts/setup_team.sh
   ```

   **To skip push confirmations (for automation):**

   ```bash
   bash scripts/setup_team.sh --yes-to-all
   ```

6. **Team Setup (Optional):** The `setup_team` script will:
   - This step is optional for solo or local-only work
   - It creates the `beads-sync` branch and may push it to the remote
   - Run `bd doctor --fix` to resolve common issues
   - Configure git remote (prompts if not set)
   - **Synchronize with remote repository** (handles divergent histories automatically)
   - Create and push `beads-sync` branch for team collaboration
   - Set up git hooks and upstream tracking
   - Perform initial sync

   **Push Safety:**
   - Before pushing anything to remote, the script will show what it's about to push
   - You'll be asked to confirm each push operation (y/n)
   - Use `-YesToAll` (PowerShell) or `--yes-to-all` (bash) to skip confirmations for automated setups
   - If no commits exist and the working tree has files, the script will prompt to create an initial commit

   **Remote Synchronization:**
   - If the remote repository was initialized with files (README, LICENSE, etc.), the script automatically merges using `--allow-unrelated-histories`
   - If merge conflicts occur, the script will exit with clear instructions to resolve them manually
   - After resolving conflicts, simply re-run the setup_team script

   **Common Scenarios:**
   - Fresh local repo + empty remote → Works automatically
   - Fresh local repo + remote with README → Automatically merges
   - Existing local commits + empty remote → Pushes local commits
   - Existing local commits + remote with files → Merges and resolves conflicts if needed

7. **VS Code Integration:** The bootstrap script automatically creates `.vscode/settings.json` with workspace-specific PATH configuration, enabling the VS Code Beads extension to find the local daemon.

8. **Confirmation:** After successful initialization, inform the user they can now create a plan using `templates/plan_template.md`

9. **Post-initialization workflow:**
   - Ask the user for their first feature
   - Create a plan file in `plans/` based on `templates/plan_template.md`
   - Ask if the plan is ready to create Beads from it
   - If yes, convert the plan to JSONL, import into Beads, and ask which Bead to start first

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

Beads supports these issue types: `epic`, `feature`, `task`, `bug`, `chore`, `merge-request`, `molecule`.
Most commonly used: `feature`, `task`, `bug`, `epic`, `chore`.
Always include a description.

```powershell
bd create "Title" --description "Context" -p 2 -t feature --json
bd create "Task" --description "Parent: Feature Title" -p 2 -t task --json
bd create "Bug Fix" --description "Issue description" -p 1 -t bug --json
bd create "Epic Title" --description "Large scope work" -p 1 -t epic --json
bd create "Chore" --description "Maintenance task" -p 3 -t chore --json
bd update <id> --status in_progress
bd close <id> --reason "Done"
```

## Plan to Beads Workflow

Convert structured plans into Beads issues automatically using the plan template and parser.

**Template Structure:**
The plan template uses a hierarchical format:

- `### Feature: Title [P1]` - Top-level feature with priority
- `- Task: Title [P2]` - Tasks under features
- `- Subtask: Title [P3]` - Subtasks under tasks
- `- Notes: Context` - Additional context for any level

**Complete Workflow:**

1. **Create a plan file:**

   ```powershell
   # Option 1: Create in plans folder (recommended for multiple plans)
   New-Item -ItemType Directory -Force -Path plans
   Copy-Item templates\plan_template.md plans\my-feature.md
   
   # Option 2: Create at root (for single plans)
   Copy-Item templates\plan_template.md plan.md
   ```

2. **Edit the plan file:**
   - Replace example features with your actual features
   - Add tasks under each feature
   - Set priority levels: [P1] (highest) to [P3] (lowest)
   - Add notes for implementation details or acceptance criteria
   - Break down complex tasks into multiple smaller tasks if needed

3. **Convert plan to Beads JSONL:**

   ```powershell
   # PowerShell
   .venv\Scripts\activate; python scripts\plan_to_beads.py --plan plans\my-feature.md --output plan_issues.jsonl
   ```

   ```bash
   # Bash
   source .venv/bin/activate && python scripts/plan_to_beads.py --plan plans/my-feature.md --output plan_issues.jsonl
   ```

4. **Append to Beads JSONL and import:**

   ```powershell
   # PowerShell
   Get-Content plan_issues.jsonl | Add-Content .beads\issues.jsonl
   bd sync --import
   Remove-Item plan_issues.jsonl
   ```

   ```bash
   # Bash
   cat plan_issues.jsonl >> .beads/issues.jsonl
   bd sync --import
   rm plan_issues.jsonl
   ```

5. **Verify issues were created:**

   ```powershell
   bd list
   ```

**Example Plan:**

```markdown
### Feature: User Authentication [P1]
- Notes: Users can securely log in and manage sessions
- Task: Create HTML login form [P1]
- Task: Add form validation [P1]
- Task: Implement session management [P1]
  - Notes: Use JWT tokens for stateless auth
- Task: Add logout functionality [P2]
```

This generates issues with automatic parent tracking and descriptions including the plan source.

## Release Workflow

**Recommended approach (LLM-assisted changelog):**

1. **Generate changelog draft from unreleased commits:**

   ```powershell
   .venv\Scripts\activate; python regenerate_changelog.py --preview --json
   ```

   This creates `changelog_draft.json` with all commits since the last tag, grouped by category.

2. **Agent writes polished changelog:**
   - Agent reads `changelog_draft.json`
   - Writes user-friendly changelog section for version X.Y.Z
   - Agent copies the formatted section to `changelog.md` (prepending as `## vX.Y.Z` section)

3. **Bump version and finalize release:**

   ```powershell
   .venv\Scripts\activate; python release.py patch|minor|major
   ```

   This updates `version.py` and `readme.md` to match the new version.

4. **Commit and tag:**

   ```powershell
   git add .
   git commit -m "Release vX.Y.Z"
   git tag vX.Y.Z
   git push origin main --tags
   ```

**Alternative (manual TBD placeholders):**

1. Bump version first (creates TBD placeholders):

   ```powershell
   .venv\Scripts\activate; python release.py patch|minor|major
   ```

2. Manually edit `changelog.md` to replace TBD sections.

3. Commit and tag as above.

**Key files:**

- `regenerate_changelog.py` - Generate changelog drafts or TBD placeholders
- `release.py` - Auto-bump version in version.py, readme.md, and changelog.md
- `changelog_draft.json` - Structured commit data for LLM processing (temporary file)

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
