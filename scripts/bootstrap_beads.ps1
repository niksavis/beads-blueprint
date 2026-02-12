<#
.SYNOPSIS
    Bootstrap Beads issue tracker for this project.

.DESCRIPTION
    Downloads and installs Beads binary to tools/bin/, configures git merge driver.
    Auto-detects platform and architecture.

.USAGE
    PowerShell 7 (pwsh) or PowerShell 5+ with scripts enabled:
        & .\scripts\bootstrap_beads.ps1
    
    NEVER use: powershell -ExecutionPolicy Bypass -File scripts\bootstrap_beads.ps1
    That spawns Windows PowerShell 5.1 which may have stricter execution policies.
    Always run in your current shell session.

.MANUAL INSTALLATION
    If execution policy completely blocks scripts:
    1. Download latest release from: https://github.com/steveyegge/beads/releases/latest
    2. Extract bd.exe (Windows) or bd (Unix) to tools/bin/
    3. Run: git config merge.beads.driver "bd merge %A %O %B %A --debug"
    4. Run: git config merge.beads.name "Beads JSONL merge"
    
    See scripts/readme.md for detailed manual installation steps.
#>

param(
    [string]$ToolsRoot,
    [switch]$SkipInstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Determine ToolsRoot: use parameter, infer from script location, or default to ./tools
if (-not $ToolsRoot) {
    if ($PSScriptRoot) {
        $ToolsRoot = Join-Path $PSScriptRoot "..\tools"
    }
    else {
        # Fallback when $PSScriptRoot is not available (e.g., when piped)
        $ToolsRoot = Join-Path (Get-Location).Path "tools"
    }
}

Write-Host "Using tools directory: $ToolsRoot" -ForegroundColor Cyan

# Check if bd is already available in PATH
if (-not $SkipInstall) {
    $bdAvailable = $null -ne (Get-Command bd -ErrorAction SilentlyContinue)
    
    if ($bdAvailable) {
        Write-Host ""
        Write-Host "Beads (bd) is already available in PATH." -ForegroundColor Yellow
        
        # Try to prompt if in interactive mode
        try {
            $Host.UI.RawUI | Out-Null
            $response = Read-Host "Skip local installation? (Y/n)"
            if ($response -eq "" -or $response -match "^[Yy]") {
                $SkipInstall = $true
                Write-Host "Using system Beads installation." -ForegroundColor Cyan
            }
        }
        catch {
            # Not interactive (piped), default to installing locally
            Write-Host "Non-interactive mode: Installing locally to ensure project has its own copy." -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

# ===== INSTALL BEADS =====
if (-not $SkipInstall) {
    Write-Host "=== Installing Beads ===" -ForegroundColor Green
    
    # Detect OS
    $platform = $null
    if ($IsWindows -or $env:OS -match "Windows") {
        $platform = "windows"
    }
    elseif ($IsMacOS) {
        $platform = "darwin"
    }
    elseif ($IsLinux) {
        $platform = "linux"
    }
    else {
        Write-Host "Unable to detect operating system." -ForegroundColor Red
        Write-Host "Supported platforms: windows, darwin (macOS), linux, freebsd" -ForegroundColor Yellow
        Write-Host "To build from source, see: https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" -ForegroundColor Cyan
        throw "Unsupported operating system"
    }

    # Detect architecture - use environment variable first (works when piped)
    $arch = $null
    if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64" -or $env:PROCESSOR_ARCHITEW6432 -eq "AMD64") {
        $arch = "amd64"
    }
    elseif ($env:PROCESSOR_ARCHITECTURE -eq "ARM64" -or $env:PROCESSOR_ARCHITEW6432 -eq "ARM64") {
        $arch = "arm64"
    }
    else {
        # Fallback to .NET detection
        $archInfo = try { [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture } catch { $null }
        if ($archInfo) {
            switch ($archInfo) {
                "X64" { $arch = "amd64" }
                "Arm64" { $arch = "arm64" }
                default {
                    Write-Host "Unsupported architecture: $archInfo" -ForegroundColor Red
                    Write-Host "Supported architectures: amd64 (x64), arm64" -ForegroundColor Yellow
                    Write-Host "To build from source, see: https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" -ForegroundColor Cyan
                    throw "Unsupported architecture: $archInfo"
                }
            }
        }
        else {
            Write-Host "Could not detect system architecture." -ForegroundColor Red
            Write-Host "Environment: PROCESSOR_ARCHITECTURE=$($env:PROCESSOR_ARCHITECTURE)" -ForegroundColor Yellow
            Write-Host "To build from source, see: https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" -ForegroundColor Cyan
            throw "Could not detect system architecture"
        }
    }

    Write-Host "Detected platform: $platform-$arch" -ForegroundColor Cyan

    # Fetch latest release
    $apiUrl = "https://api.github.com/repos/steveyegge/beads/releases/latest"
    Write-Host "Fetching latest release..." -ForegroundColor Cyan
    $release = Invoke-RestMethod -Uri $apiUrl -Headers @{ "User-Agent" = "beads-template" }

    # Extract version (remove 'v' prefix)
    $version = $release.tag_name -replace '^v', ''
    Write-Host "Latest version: $version" -ForegroundColor Green

    # Build expected asset name: beads_{version}_{platform}_{arch}.{ext}
    $extension = if ($platform -eq "windows") { "zip" } else { "tar.gz" }
    $assetName = "beads_${version}_${platform}_${arch}.${extension}"
    Write-Host "Looking for asset: $assetName" -ForegroundColor Cyan

    # Find the specific asset
    $asset = $release.assets | Where-Object {
        $_.name -eq $assetName
    } | Select-Object -First 1

    if (-not $asset) {
        Write-Host "No prebuilt binary found for $platform-$arch" -ForegroundColor Red
        Write-Host "Expected asset: $assetName" -ForegroundColor Yellow
        Write-Host "" 
        Write-Host "Beads supports:" -ForegroundColor Cyan
        Write-Host "  - Windows: amd64, arm64" -ForegroundColor Cyan
        Write-Host "  - macOS (darwin): amd64, arm64" -ForegroundColor Cyan
        Write-Host "  - Linux: amd64, arm64" -ForegroundColor Cyan
        Write-Host "  - FreeBSD: amd64" -ForegroundColor Cyan
        Write-Host "  - Android: arm64" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To build from source for your platform:" -ForegroundColor Yellow
        Write-Host "  https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" -ForegroundColor Cyan
        throw "No asset found for $platform-$arch"
    }

    $binDir = Join-Path $ToolsRoot "bin"

    # Download archive
    $archivePath = Join-Path $env:TEMP ("beads-" + $release.tag_name + "." + $extension)
    Write-Host "Downloading from $($asset.browser_download_url)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $archivePath

    # Clean and recreate bin directory if Force is set
    if ($Force -and (Test-Path $binDir)) {
        Remove-Item -Recurse -Force $binDir
    }

    New-Item -ItemType Directory -Path $binDir -Force | Out-Null

    # Extract directly to tools/bin/
    Write-Host "Extracting to $binDir..." -ForegroundColor Cyan
    if ($extension -eq "zip") {
        Expand-Archive -Force -Path $archivePath -DestinationPath $binDir
    }
    else {
        # For .tar.gz on macOS/Linux, use tar
        tar -xzf $archivePath -C $binDir
    }

    # Verify bd executable exists
    $bdPath = if ($platform -eq "windows") { Join-Path $binDir "bd.exe" } else { Join-Path $binDir "bd" }
    if (-not (Test-Path $bdPath)) {
        throw "Could not find bd executable at $bdPath after extraction."
    }

    # Make executable on Unix (if needed)
    if ($platform -ne "windows") {
        chmod +x $bdPath
    }

    Write-Host ""
    Write-Host "Beads installed successfully!" -ForegroundColor Green
    Write-Host "Binary: $bdPath" -ForegroundColor Cyan
}

# ===== CONFIGURE VS CODE =====
if (-not $SkipInstall) {
    Write-Host ""
    Write-Host "=== Configuring VS Code ===" -ForegroundColor Green
    
    # Determine repo root
    $repoRoot = (Get-Location).Path
    
    # Create .vscode directory if it doesn't exist
    $vscodeDir = Join-Path $repoRoot ".vscode"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }
    
    # Create or update workspace settings
    $settingsPath = Join-Path $vscodeDir "settings.json"
    $settingsContent = @{
        "terminal.integrated.env.windows" = @{
            "PATH" = "`${env:PATH};`${workspaceFolder}\tools\bin"
        }
    }
    
    if (Test-Path $settingsPath) {
        # Merge with existing settings
        try {
            $existingSettings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
            if (-not $existingSettings.ContainsKey("terminal.integrated.env.windows")) {
                $existingSettings["terminal.integrated.env.windows"] = $settingsContent["terminal.integrated.env.windows"]
                $existingSettings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
                Write-Host "Added terminal PATH configuration to existing workspace settings" -ForegroundColor Cyan
            }
            else {
                Write-Host "Terminal PATH configuration already exists in workspace settings" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "Warning: Could not parse existing settings.json. Skipping VS Code configuration." -ForegroundColor Yellow
        }
    }
    else {
        # Create new settings file
        $settingsContent | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
        Write-Host "Created workspace settings with terminal PATH configuration" -ForegroundColor Cyan
        Write-Host "VS Code Beads extension will now find the local daemon" -ForegroundColor Green
    }

    # Create or update workspace tasks to start the Beads daemon
    $tasksPath = Join-Path $vscodeDir "tasks.json"
    $taskLabel = "Start Beads Daemon with Auto-Sync"
    $taskDefinition = @{
        "label"          = $taskLabel
        "type"           = "shell"
        "command"        = "bd daemon start --auto-commit"
        "isBackground"   = $true
        "problemMatcher" = @()
        "presentation"   = @{
            "echo"             = $false
            "reveal"           = "never"
            "focus"            = $false
            "panel"            = "shared"
            "showReuseMessage" = $false
            "clear"            = $false
        }
        "options"        = @{
            "env" = @{
                "PATH" = "`${env:PATH};`${workspaceFolder}\tools\bin"
            }
        }
        "runOptions"     = @{
            "runOn" = "folderOpen"
        }
    }

    if (Test-Path $tasksPath) {
        try {
            $existingTasks = Get-Content $tasksPath -Raw | ConvertFrom-Json -AsHashtable
            if (-not $existingTasks.ContainsKey("tasks")) {
                $existingTasks["tasks"] = @()
            }

            $taskExists = $false
            foreach ($task in $existingTasks["tasks"]) {
                if ($task.label -eq $taskLabel) {
                    $taskExists = $true
                    break
                }
            }

            if (-not $taskExists) {
                $existingTasks["version"] = "2.0.0"
                $existingTasks["tasks"] += $taskDefinition
                $existingTasks | ConvertTo-Json -Depth 10 | Set-Content $tasksPath
                Write-Host "Added Beads daemon task to existing tasks.json" -ForegroundColor Cyan
            }
            else {
                Write-Host "Beads daemon task already exists in tasks.json" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "Warning: Could not parse existing tasks.json. Skipping task configuration." -ForegroundColor Yellow
        }
    }
    else {
        $tasksContent = @{
            "version" = "2.0.0"
            "tasks"   = @($taskDefinition)
        }

        $tasksContent | ConvertTo-Json -Depth 10 | Set-Content $tasksPath
        Write-Host "Created tasks.json to start the Beads daemon on folder open" -ForegroundColor Cyan
    }
}

# ===== CONFIGURE GIT =====
Write-Host ""
Write-Host "=== Configuring Git ===" -ForegroundColor Green

# Determine repo root
$repoRoot = (Get-Location).Path

# Try to find .git directory to confirm we're in a git repo
$gitDir = Join-Path $repoRoot ".git"
if (-not (Test-Path $gitDir)) {
    Write-Host "Warning: Not in a git repository root. Looking for parent..." -ForegroundColor Yellow
    # Try parent directories
    $currentDir = $repoRoot
    for ($i = 0; $i -lt 3; $i++) {
        $parent = Split-Path $currentDir -Parent
        if ([string]::IsNullOrWhiteSpace($parent)) {
            break
        }
        if (Test-Path (Join-Path $parent ".git")) {
            $repoRoot = $parent
            Write-Host "Found git repository at: $repoRoot" -ForegroundColor Cyan
            Set-Location $repoRoot
            break
        }
        if ($parent -eq $currentDir) {
            break
        }
        $currentDir = $parent
    }
}

$gitDir = Join-Path $repoRoot ".git"
if (Test-Path $gitDir) {
    git config merge.beads.name "Beads JSONL merge"
    git config merge.beads.driver "bd merge %A %O %B %A --debug"
    Write-Host "Configured git merge driver for .beads/issues.jsonl" -ForegroundColor Cyan
}
else {
    $didInit = $false
    try {
        $Host.UI.RawUI | Out-Null
        $response = Read-Host "No .git found. Initialize a git repository here? (y/n)"
        if ($response -match "^[Yy]") {
            git init 2>&1 | Out-String | Write-Host
            $didInit = $true
        }
    }
    catch {
        # Non-interactive mode
    }

    $gitDir = Join-Path $repoRoot ".git"
    if ($didInit -and (Test-Path $gitDir)) {
        git config merge.beads.name "Beads JSONL merge"
        git config merge.beads.driver "bd merge %A %O %B %A --debug"
        Write-Host "Configured git merge driver for .beads/issues.jsonl" -ForegroundColor Cyan
    }
    else {
        Write-Host "Warning: Not a git repository. Skipping git merge driver configuration." -ForegroundColor Yellow
        Write-Host "Missing features until git is initialized:" -ForegroundColor Yellow
        Write-Host "- Git merge driver for .beads/issues.jsonl" -ForegroundColor Yellow
        Write-Host "- Repository and clone IDs during bd init" -ForegroundColor Yellow
        Write-Host "- Team setup and sync workflows" -ForegroundColor Yellow
        Write-Host "To enable later: run 'git init', then rerun bootstrap_beads.ps1 or configure_beads.ps1." -ForegroundColor Yellow
    }
}

# ===== VERIFICATION =====
Write-Host ""
Write-Host "=== Verification ===" -ForegroundColor Green

if (-not $SkipInstall) {
    $binDir = Join-Path $ToolsRoot "bin"
    $bdPath = if ($platform -eq "windows") { Join-Path $binDir "bd.exe" } else { Join-Path $binDir "bd" }

    if (Test-Path $bdPath) {
        & $bdPath --version
        Write-Host ""
        Write-Host "To use this local installation, add to PATH:" -ForegroundColor Yellow
        Write-Host "  `$env:Path += `";$binDir`"" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Or invoke directly:" -ForegroundColor Yellow
        Write-Host "  & $bdPath init" -ForegroundColor Cyan
    }
    else {
        Write-Host "Warning: Beads installed, but binary not found at expected location." -ForegroundColor Yellow
    }
}
else {
    bd --version
}

Write-Host ""
Write-Host "Bootstrap complete!" -ForegroundColor Green