# Beads Blueprint Template

Create new local repo from template with one command.

Run command from parent folder where new project folder should be created.

## Prerequisites

- Required for project creation:
  - Git
- Required to start environment bootstrap:
  - Python available in PATH
- During bootstrap:
  - `scripts/initialize_environment.py` auto-selects Python 3.14+ for `.venv`
  - Node.js 20+ and npm are auto-installed when platform package managers are available
- Optional for AI-guided setup:
  - VS Code with GitHub Copilot Chat

## One-Line Project Creation

### Linux or Git Bash

Default project name (`my-project`):

```bash
curl -sSL https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.sh | bash
```

Custom project name:

```bash
curl -sSL https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.sh | PROJECT_NAME="my-project" bash
```

Custom project name + local git identity:

```bash
curl -sSL https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.sh | PROJECT_NAME="my-project" GIT_NAME="John Smith" GIT_EMAIL="john.smith@email.com" bash
```

### Windows PowerShell

Default project name (`my-project`):

```powershell
irm https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.ps1 | iex
```

Custom project name:

```powershell
$env:PROJECT_NAME='my-project'; irm https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.ps1 | iex
```

Custom project name + local git identity:

```powershell
$env:PROJECT_NAME='my-project'; $env:GIT_NAME='John Smith'; $env:GIT_EMAIL='john.smith@email.com'; irm https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.ps1 | iex
```

## Parameters

- `PROJECT_NAME`: local folder/repo name (default: `my-project`)
- `GIT_NAME`: local git author name for new repo only
- `GIT_EMAIL`: local git author email for new repo only
- `TEMPLATE_URL`: override template repo source (default: `https://github.com/niksavis/beads-blueprint.git`)

## Git Identity Policy

- Script never writes global git config.
- If you pass `GIT_NAME` or `GIT_EMAIL`, script sets them with `git config --local` in new repo only.
- If commit identity is available (from `GIT_*` values or existing git config), script creates initial commit.
- If identity is not available, script skips initial commit and prints local-only commands.

## Next Step In Copilot Chat

After project is created and opened in VS Code, paste:

```text
You are in repository root of a fresh project created from beads-blueprint.
Bootstrap local development environment end-to-end.

Do these steps in order:
1) Run: python scripts/initialize_environment.py
  If `python` is unavailable on Windows but `py` exists, run: py -3 scripts/initialize_environment.py
2) Ensure Python packages came from requirements.txt and requirements-dev.txt lock files.
3) Verify Node.js 20+ and npm are available.
4) Verify Beads and Dolt are installed and available in PATH.
5) Run fast validation and hook checks.

Final checks (report pass/fail for each):
node --version
npm --version
bd --version
dolt version
python validate.py --fast
python install_hooks.py --check
bd info --json
bd config list

Rules:
- Do not change global git config.
- If any step fails, fix it and continue.
- Do not require VS Code UI actions for venv creation.
- If setup changes `.gitignore` or `.beads/hooks/*` in your real project repo, commit those files in the same setup commit.
- Optional tightening: verify Beads config contains `issue-prefix`, `issue_prefix`, or `id.prefix`, and the value matches repository folder slug.
- Do not edit always-on policy files (`.github/copilot-instructions.md`, `agents.md`) during setup.
- End with exact next command I should run.
- If a VS Code window for this repository is open, trigger `workbench.action.reloadWindow` after successful verification.
- After successful verification, last sentence must be: If VS Code did not reload automatically, restart VS Code now so extensions and tooling load correctly.
```

## Manual Fallback (No AI)

```bash
python scripts/initialize_environment.py || py -3 scripts/initialize_environment.py
node --version && npm --version && bd --version
python validate.py --fast || py -3 validate.py --fast
python install_hooks.py --check || py -3 install_hooks.py --check
```

## Security Note

If you do not want to pipe remote scripts directly, download and inspect first:

```bash
curl -sSLo new-project.sh https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.sh
bash new-project.sh
```

```powershell
iwr https://raw.githubusercontent.com/niksavis/beads-blueprint/main/scripts/new-project.ps1 -OutFile new-project.ps1
powershell -ExecutionPolicy Bypass -File .\new-project.ps1
```

## License

MIT. See `LICENSE`.
