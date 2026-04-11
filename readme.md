# Beads Blueprint Template

Create new local repo from template with one command.

Run command from parent folder where new project folder should be created.

## Prerequisites

- Required for project creation:
  - Git
- Required for full environment bootstrap after creation:
  - Python 3.14+
  - Node.js 20+
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
1) Run: python scripts/initialize_environment.py --yes-to-all
2) Ensure Python packages come from requirements.txt and requirements-dev.txt lock files.
3) Run: npm ci
4) Verify Beads and Dolt are installed and available in PATH.
5) Run fast validation and hook checks.

Final checks (report pass/fail for each):
bd --version
dolt version
python validate.py --fast
python install_hooks.py --check

Rules:
- Do not change global git config.
- If any step fails, fix it and continue.
- End with exact next command I should run.
```

## Manual Fallback (No AI)

```bash
python scripts/initialize_environment.py --yes-to-all && bd --version && python validate.py --fast && python install_hooks.py --check
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
