---
name: dev-tools-setup
description: >
  Use when setting up a new machine or fixing missing CLI tooling (rg/ripgrep, fd, jq, yq,
  GitHub Copilot CLI). Includes install and verification commands for Windows (winget, no admin),
  macOS (Homebrew), and Linux (apt/pacman/cargo).
---

# Skill: Dev Tools Setup

Install and verify optional development tools that improve contributor experience.

## Tool Registry

### ripgrep (`rg`)

Ultra-fast regex search. Used by VS Code for workspace search and by AI agents (GitHub Copilot)
to locate symbols quickly. Respects `.gitignore` — critical for large repos.

| Platform                   | Command                                  |
| -------------------------- | ---------------------------------------- |
| Windows (winget, no admin) | `winget install BurntSushi.ripgrep.MSVC` |
| macOS (Homebrew)           | `brew install ripgrep`                   |
| Linux Debian/Ubuntu        | `sudo apt-get install ripgrep`           |
| Linux Arch                 | `sudo pacman -S ripgrep`                 |
| Linux (any) via cargo      | `cargo install ripgrep`                  |

Verify: `rg --version`

Common usage:

```bash
rg "def send_email"          # find function definition across repo
rg "assignee_email" app/     # scoped search
rg -t py "except Exception"  # Python files only — find broad excepts
```

---

### jq

JSON pretty-printer and filter. Essential for reading JSON-Lines log output.

| Platform                   | Command                    |
| -------------------------- | -------------------------- |
| Windows (winget, no admin) | `winget install jqlang.jq` |
| macOS (Homebrew)           | `brew install jq`          |
| Linux Debian/Ubuntu        | `sudo apt-get install jq`  |

Verify: `jq --version`

Usage with repository logs:

```bash
# PowerShell: pretty-print JSON log stream (stderr suppressed)
python run.py dev 2>$null | jq .

# PowerShell: filter only WARNING and above
python run.py dev 2>$null | jq 'select(.level == "WARNING" or .level == "ERROR")'

# PowerShell: follow live log file
Get-Content logs/app.log -Wait | ForEach-Object { $_ | jq . }

# bash/macOS/Linux equivalents
python run.py dev 2>/dev/null | jq .
tail -f logs/app.log | jq .
```

---

### yq

YAML query and transformation CLI. Useful for inspecting Kubernetes manifests,
compose files, and other YAML configs.

| Platform                   | Command                       |
| -------------------------- | ----------------------------- |
| Windows (winget, no admin) | `winget install MikeFarah.yq` |
| macOS (Homebrew)           | `brew install yq`             |
| Linux Debian/Ubuntu        | `sudo snap install yq`        |

Verify: `yq --version`

Common usage:

```bash
yq '.services.web.image' docker-compose.local.yml
yq '.metadata.name' k8s/deployment.yaml
yq '.[] | select(.priority <= 1)' sample.yaml
```

---

### GitHub Copilot CLI (`copilot`)

Standalone AI coding agent in the terminal. The old `gh copilot` extension is retired; Copilot
CLI is now an independent tool installed directly.

**Requires** an active GitHub Copilot subscription.

| Platform                     | Command                                            |
| ---------------------------- | -------------------------------------------------- |
| Windows (winget, no admin)   | `winget install GitHub.Copilot`                    |
| macOS (Homebrew)             | `brew install copilot-cli`                         |
| All platforms (npm)          | `npm install -g @github/copilot`                   |
| macOS/Linux (install script) | `curl -fsSL https://gh.io/copilot-install \| bash` |

Verify: `copilot --version`

On first launch, run `copilot` and use the `/login` slash command to authenticate with GitHub.

Usage:

```bash
copilot                                      # interactive session
copilot -p "explain git rebase -i HEAD~3"   # single prompt (programmatic)
copilot -p "delete all merged local branches" --allow-tool shell
```

---

### fd (`fd-find`)

Faster alternative to `find`. Optional but useful for file discovery.

| Platform                   | Command                        |
| -------------------------- | ------------------------------ |
| Windows (winget, no admin) | `winget install sharkdp.fd`    |
| macOS (Homebrew)           | `brew install fd`              |
| Linux Debian/Ubuntu        | `sudo apt-get install fd-find` |

Verify: `fd --version`

---

## Installation Workflow

When a user reports a tool is missing or asks how to install it:

1. Identify the tool from the Tool Registry above.
2. Detect platform: Windows → winget; macOS → brew; Linux → apt or pacman.
3. Provide the single-line install command from the registry.
4. Run the verify command to confirm installation.
5. If the user is on Windows and lacks admin: all `winget` commands above work without admin.

## Troubleshooting

### winget not found (Windows)

winget ships with Windows 10 1709+ and Windows 11. If missing:

- Open Microsoft Store → search "App Installer" → install it.
- Or check: `Get-AppxPackage Microsoft.DesktopAppInstaller`

### brew not found (macOS)

Install Homebrew first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Copilot CLI not authenticating

On first launch, run `copilot` interactively and enter `/login` to authenticate with GitHub.
Ensure your account has an active GitHub Copilot subscription.

### cargo not in PATH (for Rust tools)

Install Rust toolchain:

- Windows/macOS/Linux: `curl https://sh.rustup.rs -sSf | sh`
- Windows (winget): `winget install Rustlang.Rustup`
