# Beads Blueprint Template

Template repository for structured planning and execution using Beads. It provides
minimal but complete tooling to turn a plan into Beads issues, track work, and
prepare releases with a changelog and version bump.

**Version:** 0.1.0

## What This Template Includes

- README, agents.md, changelog.md, license, gitignore, gitattributes
- Pre-configured `.beads` folder with proper `.gitignore` (Beads initialization still required)
- Copilot instructions with Beads workflow guidance
- PowerShell and bash bootstrap scripts to install/configure Beads from the latest release
- Plan template and parser that generates Beads JSONL for batch import
- LLM-assisted changelog generation with JSON export for agent processing
- Release scripts that bump version and auto-update readme.md

## Quick Start (Any Shell)

### Setup Python Environment

Create a virtual environment and install tooling:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Install Beads

**If Beads is already installed elsewhere** (e.g., globally or in `D:\Development\tools\bd`),
just configure the git merge driver:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\configure_beads.ps1
```

```bash
./scripts/configure_beads.sh
```

**If you need to install Beads locally**, the bootstrap script downloads the latest release
and extracts `bd` (or `bd.exe` on Windows) directly to `tools/bin/`. This avoids PATH length issues.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\bootstrap_beads.ps1
```

```bash
./scripts/bootstrap_beads.sh
```

**After local installation, choose one of these options:**

### Option 1: Add to PATH (recommended for terminal use)

PowerShell (session):

```powershell
$env:Path += ";$PWD\tools\bin"
bd --version
```

bash (session):

```bash
export PATH="$PWD/tools/bin:$PATH"
bd --version
```

### Option 2: Configure VS Code (no PATH modification, no admin rights)

Create or edit `.vscode/settings.json` in your workspace:

```json
{
  "terminal.integrated.env.windows": {
    "PATH": "${workspaceFolder}\\tools\\bin;${env:PATH}"
  },
  "terminal.integrated.env.linux": {
    "PATH": "${workspaceFolder}/tools/bin:${env:PATH}"
  }
}
```

This makes `bd` available in all VS Code terminals without modifying system PATH.

### Option 3: Invoke directly

Windows:

```powershell
tools\bin\bd.exe --version
```

Linux/macOS:

```bash
tools/bin/bd --version
```

**Tools Directory Structure:**

The `tools/bin/` directory contains locally installed CLI tools to avoid PATH length issues.
You only add `tools/bin` to PATH once, avoiding the ~2000 character limit. To add more
CLI tools, extract them directly to `tools/bin/` following the same pattern.

**To skip installation with bootstrap** (only configure): Add `-SkipInstall` flag (PowerShell)
or `--skip-install` argument (bash).

### Initialize Beads

After installing or configuring Beads, initialize the repository:

```powershell
bd init
```

```bash
bd init
```

This creates the necessary files (`issues.jsonl`, etc.) in the `.beads` folder.

### Create and Execute a Plan

1. Create a plan using the template:

   ```powershell
   New-Item -ItemType Directory -Force -Path plans
   Copy-Item templates\plan_template.md plans\my-feature.md
   ```

2. Edit your plan file with features and tasks

3. Convert plan to Beads JSONL:

   ```powershell
   python scripts\plan_to_beads.py --plan plans\my-feature.md --output plan_issues.jsonl
   ```

4. Import into Beads:

   ```powershell
   Get-Content plan_issues.jsonl | Add-Content .beads\issues.jsonl
   bd sync --import
   Remove-Item plan_issues.jsonl
   ```

5. Verify issues were created:

   ```powershell
   bd list
   ```

**Note:** If you haven't added `tools/bin` to PATH, use `tools\bin\bd` for PowerShell
or `tools/bin/bd` for bash in your commands.

## Plan to Beads Workflow

The template expects a plan organized by Features, Tasks, and Subtasks. The parser
generates Beads JSONL format for efficient batch import with automatic parent tracking.

Plan format highlights:

- `### Feature: <title> [P1]` - Creates a feature with priority (P1-P3)
- `- Task: <title> [P2]` - Creates a task under the current feature
- `- Subtask: <title> [P3]` - Creates a subtask under the current task
- `- Notes: <context>` - Adds notes/context to features or tasks

The parser embeds parent references in descriptions for easy tracing.

See [templates/plan_template.md](templates/plan_template.md) for the full format and examples.

## Release Preparation

**Recommended (LLM-assisted changelog):**

1. Generate changelog draft from unreleased commits:

   ```powershell
   python regenerate_changelog.py --preview --json
   ```

   This creates `changelog_draft.json` with commits since the last tag.

2. Ask your LLM/Agent to write a polished changelog section by reading the JSON file, then copy the output to `changelog.md` as a new `## vX.Y.Z` section at the top.

3. Bump the version (updates version.py and readme.md):

   ```powershell
   python release.py patch    # 0.1.0 → 0.1.1
   python release.py minor    # 0.1.0 → 0.2.0
   python release.py major    # 0.1.0 → 1.0.0
   ```

4. Commit and tag:

   ```powershell
   git add .
   git commit -m "Release vX.Y.Z"
   git tag vX.Y.Z
   git push origin main --tags
   ```

**Alternative (manual TBD placeholders):**

Run `python release.py patch` which creates a changelog section with TBD placeholders, then manually edit `changelog.md` to replace them before committing.

## Repository Layout

- [agents.md](agents.md) - agent workflow and Beads rules
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot guidance
- [scripts/](scripts/) - bootstrap and plan tooling
- [templates/](templates/) - plan templates

## License

MIT. See [LICENSE](LICENSE).
