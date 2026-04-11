# Scripts

This folder contains Python-first automation scripts for the template.
Repository tooling also requires Node.js for markdown quality checks.

## Environment and Setup

- `new-project.sh`
  - One-line bootstrap entry point for Linux/Git Bash (`curl ... | bash`)
  - Creates local project from template and initializes a fresh git history
  - Any provided `GIT_NAME`/`GIT_EMAIL` values are applied with `git config --local`
  - Supports optional parameters via environment variables:
    - `PROJECT_NAME`
    - `GIT_NAME`
    - `GIT_EMAIL`
    - `TEMPLATE_URL`

- `new-project.ps1`
  - One-line bootstrap entry point for Windows PowerShell (`irm ... | iex`)
  - Creates local project from template and initializes a fresh git history
  - Any provided `GIT_NAME`/`GIT_EMAIL` values are applied with `git config --local`
  - Supports optional parameters via environment variables:
    - `PROJECT_NAME`
    - `GIT_NAME`
    - `GIT_EMAIL`
    - `TEMPLATE_URL`

- `initialize_environment.py`
  - End-to-end environment bootstrap:
    - discover Python 3.14+ and create/update `.venv`
    - install Python dependencies and tooling
    - ensure Node.js 20+ and install Node tooling (`npm ci`) used by markdown quality checks
    - bootstrap Beads
    - install hooks
    - run fast validation

- `bootstrap_beads.py`
  - Installs or verifies Beads and Dolt
  - Configures VS Code settings/tasks
  - Configures git merge driver for Beads JSONL merges

- `install_beads.py`
  - Installs Beads from `gastownhall/beads` release assets
  - Installs Dolt from `dolthub/dolt` release assets
  - Ensures Windows user PATH includes:
    - `%LOCALAPPDATA%\\Programs\\bd`
    - `%LOCALAPPDATA%\\Programs\\dolt`
  - Prompts optional updates when both tools already exist

- `configure_beads.py`
  - Configures git merge settings for `.beads/issues.jsonl`

## Usage

### Full environment setup

```bash
python scripts/initialize_environment.py
```

### Setup without Node tooling (temporary)

```bash
python scripts/initialize_environment.py --skip-node-tools
```

Use this only when Node.js is unavailable. Install Node.js 20+, run `npm ci`,
then rerun `python validate.py --fast`.

### Beads bootstrap only

```bash
python scripts/bootstrap_beads.py
```

If Beads initialization adds ignore entries (for example Dolt/Beads artifacts) to
`.gitignore` in a real project repository, commit that `.gitignore` update.

### Optional Beads and Dolt upgrade

```bash
python scripts/bootstrap_beads.py --update-tools
```

## Design Rules

- Setup automation scripts in this template are Python-first for cross-platform consistency.
- Node tooling is required for markdown quality checks.
- Shell wrappers are supported for one-line project creation UX.
- Plan conversion is intentionally not scripted in this template.
