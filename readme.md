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
- A plan template and parser that generates Beads commands
- Simple release scripts that bump version and scaffold changelog entries

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
   Copy-Item -Force templates\plan_template.md plan.md
   ```

1. Generate Beads commands from the plan:

   ```powershell
   python scripts\plan_to_beads.py --plan plan.md --output beads_commands.ps1
   ```

1. Review and run the generated commands:

   ```powershell
   powershell -ExecutionPolicy Bypass -File beads_commands.ps1
   ```

**Note:** If you haven't added `tools/bin` to PATH, use `tools\bin\bd` for PowerShell
or `tools/bin/bd` for bash in your commands.

## Plan to Beads Workflow

The template expects a plan organized by Features, Tasks, and Subtasks. The parser
creates Beads issues with types `feature`, `task`, and `subtask` and embeds parent
references in the description for easy tracing.

Plan format highlights:

- `### Feature: <title>` starts a feature block
- `- Task: <title>` creates a task under the current feature
- `- Subtask: <title>` creates a subtask under the current task

See [templates/plan_template.md](templates/plan_template.md) for the full format.

## Release Preparation

1. Update the changelog section for the new version:

   ```powershell
   python regenerate_changelog.py --version 0.1.1
   ```

   ```bash
   python regenerate_changelog.py --version 0.1.1
   ```

1. Bump the version and refresh README version:

   ```powershell
   python release.py patch
   ```

   ```bash
   python release.py patch
   ```

## Repository Layout

- [agents.md](agents.md) - agent workflow and Beads rules
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot guidance
- [scripts/](scripts/) - bootstrap and plan tooling
- [templates/](templates/) - plan templates

## License

MIT. See [LICENSE](LICENSE).
