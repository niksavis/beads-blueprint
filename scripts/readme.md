# Scripts

This folder contains Python-only automation scripts for the template.

## Environment and Setup

- `initialize_environment.py`
  - End-to-end environment bootstrap:
    - create/update `.venv`
    - install dependencies and tooling
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
python scripts/initialize_environment.py --yes-to-all
```

### Beads bootstrap only

```bash
python scripts/bootstrap_beads.py
```

### Optional Beads and Dolt upgrade

```bash
python scripts/bootstrap_beads.py --update-tools
```

## Design Rules

- Scripts in this template are Python-only for cross-platform consistency.
- No PowerShell or bash setup scripts are used.
- Plan conversion is intentionally not scripted in this template.
