# Scripts

This folder contains bootstrap and conversion scripts for the Beads template.

## Beads Installation

### Automated Installation

- **install_beads.ps1**: Download and install the latest Beads release (PowerShell).
- **configure_beads.ps1**: Configure git merge driver for .beads/issues.jsonl (PowerShell).
- **bootstrap_beads.ps1**: Runs install + configure and verifies bd (PowerShell).
- **install_beads.sh**: Download and install the latest Beads release (bash).
- **configure_beads.sh**: Configure git merge driver for .beads/issues.jsonl (bash).
- **bootstrap_beads.sh**: Runs install + configure and verifies bd (bash).

The bootstrap scripts also create a VS Code task to start the Beads daemon on folder open:

- Task label: Start Beads Daemon with Auto-Sync
- Command: bd daemon start --auto-commit --auto-push
- Task file: .vscode/tasks.json (created if missing)

### Team Setup

- **setup_team.ps1**: Configure project for team collaboration (PowerShell).
- **setup_team.sh**: Configure project for team collaboration (bash).

These scripts automate team configuration after `bd init`:

- Run `bd doctor --fix` to resolve common issues
- Set up git remote (interactive prompt if not configured)
- Create and push `beads-sync` branch for issue synchronization
- Configure git hooks and upstream tracking
- Perform initial sync to share issues with team

**Usage:**

PowerShell:

```powershell
& .\scripts\setup_team.ps1                              # Interactive mode
& .\scripts\setup_team.ps1 -RemoteUrl "https://github.com/user/repo.git"
& .\scripts\setup_team.ps1 -SkipRemote                  # For local testing
```

Bash:

```bash
bash scripts/setup_team.sh                              # Interactive mode
bash scripts/setup_team.sh --remote-url "https://github.com/user/repo.git"
bash scripts/setup_team.sh --skip-remote                # For local testing
```

**Usage:**

PowerShell:

```powershell
& .\scripts\bootstrap_beads.ps1
```

Bash:

```bash
bash scripts/bootstrap_beads.sh
```

**Important:** Always run scripts in your current shell. Never use `powershell -ExecutionPolicy Bypass -File script.ps1` as it spawns Windows PowerShell 5.1 which may have stricter execution policies.

### Manual Installation (If Scripts Are Blocked)

If execution policy completely blocks scripts, install manually:

1. **Download Beads:**
   - Visit: <https://github.com/steveyegge/beads/releases/latest>
   - Download the archive for your platform:
     - Windows x64: `beads_{version}_windows_amd64.zip`
     - Windows ARM64: `beads_{version}_windows_arm64.zip`
     - macOS Intel: `beads_{version}_darwin_amd64.tar.gz`
     - macOS Apple Silicon: `beads_{version}_darwin_arm64.tar.gz`
     - Linux x64: `beads_{version}_linux_amd64.tar.gz`

2. **Extract Binary:**
   - Create directory: `tools/bin/`
   - Extract `bd.exe` (Windows) or `bd` (Unix) to `tools/bin/`

3. **Configure Git Merge Driver:**

   ```powershell
   git config merge.beads.name "Beads JSONL merge"
   git config merge.beads.driver "bd merge %A %O %B %A --debug"
   ```

4. **Add to PATH (optional, session only):**

   ```powershell
   $env:Path += ";$PWD\tools\bin"
   ```

   Or invoke directly: `& tools\bin\bd.exe init`

5. **Initialize Beads:**

   ```powershell
   bd init
   ```

**Installation Strategy**: The archive contains `bd` (or `bd.exe` on Windows), README, and
LICENSE. These are extracted directly to `tools/bin/`. This avoids PATH length limits by
requiring only ONE directory (`tools/bin`) to be added to PATH. All future CLI tools can
use the same pattern.

**OS Detection**: The install scripts automatically detect your operating system and
architecture, then download the correct binary from the latest GitHub release:

- Platforms: Windows, macOS (darwin), Linux, FreeBSD
- Architectures: x64 (amd64), ARM64
- Archive formats: .zip (Windows), .tar.gz (all others)

**If Beads is already installed**: Run `configure_beads.ps1` or `configure_beads.sh` directly
to set up the git merge driver without installing locally. The bootstrap scripts also detect
if `bd` is already in PATH and offer to skip installation.

## Plan Conversion

- plan_to_beads.py: Converts a plan markdown file to Beads commands.
