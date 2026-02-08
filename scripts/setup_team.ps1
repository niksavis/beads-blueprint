#!/usr/bin/env pwsh
# Team Setup Script for Beads
# Configures the project for team collaboration with beads-sync branch

param(
    [string]$RemoteUrl = "",
    [switch]$SkipRemote = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
Team Setup Script for Beads

This script configures your Beads project for team collaboration:
  1. Fixes common Beads configuration issues
  2. Sets up git remote (if needed)
  3. Creates beads-sync branch for issue synchronization
  4. Configures git hooks
  5. Performs initial sync

Usage:
  .\scripts\setup_team.ps1                              # Interactive mode
  .\scripts\setup_team.ps1 -RemoteUrl <url>             # Specify remote URL
  .\scripts\setup_team.ps1 -SkipRemote                  # Skip remote setup
  .\scripts\setup_team.ps1 -Help                        # Show this help

Examples:
  .\scripts\setup_team.ps1 -RemoteUrl "https://github.com/user/repo.git"
  .\scripts\setup_team.ps1 -SkipRemote  # For local-only testing

"@
    exit 0
}

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== Beads Team Setup ===" -ForegroundColor Cyan

# Check if bd is available
$bdPath = Get-Command bd -ErrorAction SilentlyContinue
if (-not $bdPath) {
    if (Test-Path "tools\bin\bd.exe") {
        $env:Path += ";$PWD\tools\bin"
        Write-Host "Added tools\bin to PATH" -ForegroundColor Yellow
    }
    else {
        Write-Host "ERROR: bd command not found. Run bootstrap_beads.ps1 first." -ForegroundColor Red
        exit 1
    }
}

# Check if Beads is initialized
if (-not (Test-Path ".beads\beads.db")) {
    Write-Host "ERROR: Beads not initialized. Run 'bd init' first." -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 1: Running bd doctor --fix..." -ForegroundColor Green
bd doctor --fix --yes 2>&1 | Out-String | Write-Host

# Check if git remote exists
$hasRemote = git remote get-url origin 2>$null
if (-not $hasRemote -and -not $SkipRemote) {
    Write-Host "`nStep 2: Setting up git remote..." -ForegroundColor Green
    
    if (-not $RemoteUrl) {
        Write-Host "No remote configured. Please enter your git remote URL:"
        Write-Host "Example: https://github.com/user/repo.git" -ForegroundColor Yellow
        $RemoteUrl = Read-Host "Remote URL"
    }
    
    if ($RemoteUrl) {
        Write-Host "Adding remote 'origin': $RemoteUrl"
        git remote add origin $RemoteUrl
        Write-Host "Remote added successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Skipping remote setup (you can add it later with: git remote add origin <url>)" -ForegroundColor Yellow
    }
}
elseif ($hasRemote) {
    Write-Host "`nStep 2: Git remote already configured: $hasRemote" -ForegroundColor Green
}
else {
    Write-Host "`nStep 2: Skipping remote setup (--SkipRemote flag)" -ForegroundColor Yellow
}

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
if (-not $currentBranch) {
    $currentBranch = "main"
}

Write-Host "`nStep 3: Checking beads-sync branch..." -ForegroundColor Green

# Check if beads-sync branch exists locally
$hasSyncBranch = git rev-parse --verify beads-sync 2>$null
if (-not $hasSyncBranch) {
    Write-Host "Creating beads-sync branch..."
    
    # Check if we have commits
    $hasCommits = git rev-parse HEAD 2>$null
    if (-not $hasCommits) {
        Write-Host "No commits yet. Creating initial commit..."
        git add .beads/issues.jsonl
        git commit -m "chore: initialize beads" --allow-empty
    }
    
    # Create beads-sync branch
    git checkout -b beads-sync
    Write-Host "beads-sync branch created" -ForegroundColor Green
    
    # Push to remote if available
    if ($hasRemote -and -not $SkipRemote) {
        Write-Host "Pushing beads-sync to remote..."
        git push -u origin beads-sync 2>&1 | Out-String | Write-Host
    }
    
    # Return to original branch
    git checkout $currentBranch
}
else {
    Write-Host "beads-sync branch already exists" -ForegroundColor Green
}

# Set upstream for current branch if remote exists
if ($hasRemote -and -not $SkipRemote) {
    Write-Host "`nStep 4: Configuring upstream for $currentBranch..." -ForegroundColor Green
    
    $hasUpstream = git rev-parse --abbrev-ref "$currentBranch@{upstream}" 2>$null
    if (-not $hasUpstream) {
        # Check if branch exists on remote
        $remoteBranch = git ls-remote --heads origin $currentBranch 2>$null
        if ($remoteBranch) {
            Write-Host "Setting upstream to origin/$currentBranch"
            git branch --set-upstream-to=origin/$currentBranch $currentBranch
        }
        else {
            Write-Host "Pushing $currentBranch to remote..."
            git push -u origin $currentBranch 2>&1 | Out-String | Write-Host
        }
        Write-Host "Upstream configured" -ForegroundColor Green
    }
    else {
        Write-Host "Upstream already configured: $hasUpstream" -ForegroundColor Green
    }
}
else {
    Write-Host "`nStep 4: Skipping upstream configuration (no remote)" -ForegroundColor Yellow
}

Write-Host "`nStep 5: Initial Beads sync..." -ForegroundColor Green
bd sync 2>&1 | Out-String | Write-Host

Write-Host "`n=== Team Setup Complete ===" -ForegroundColor Cyan
Write-Host @"

Your Beads project is now configured for team collaboration!

Next steps:
  1. Team members should clone the repository
  2. Run: & .\scripts\bootstrap_beads.ps1
  3. Run: & .\scripts\setup_team.ps1
  4. Start creating issues: bd create "Title" --description "Description" -p 2 -t feature

Workflow:
  - Before starting work: bd sync --import (or git pull)
  - Create/update issues: bd create, bd update, bd close
  - Share changes: bd sync (exports to JSONL and commits)
  - Push to team: git push

Documentation: See agents.md for complete workflow rules.

"@ -ForegroundColor Green
