#!/usr/bin/env pwsh
# Team Setup Script for Beads
# Configures the project for team collaboration with beads-sync branch

param(
    [string]$RemoteUrl = "",
    [switch]$SkipRemote = $false,
    [switch]$YesToAll = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
Team Setup Script for Beads

This script configures your Beads project for team collaboration:
  1. Fixes common Beads configuration issues
  2. Sets up git remote (if needed)
  3. Synchronizes with remote repository (handles divergent histories)
  4. Creates beads-sync branch for issue synchronization
  5. Configures git hooks and upstream tracking
    6. Performs initial Beads sync
    7. Optionally creates an initial git commit

Usage:
  .\scripts\setup_team.ps1                              # Interactive mode
  .\scripts\setup_team.ps1 -RemoteUrl <url>             # Specify remote URL
  .\scripts\setup_team.ps1 -SkipRemote                  # Skip remote setup
  .\scripts\setup_team.ps1 -YesToAll                    # Skip all confirmations
  .\scripts\setup_team.ps1 -Help                        # Show this help

Examples:
  .\scripts\setup_team.ps1 -RemoteUrl "https://github.com/user/repo.git"
  .\scripts\setup_team.ps1 -SkipRemote  # For local-only testing

Notes:
  - If remote repository was initialized with files (README, etc.),
    the script will automatically merge with --allow-unrelated-histories
  - If merge conflicts occur, you'll be prompted to resolve them manually

"@
    exit 0
}

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== Beads Team Setup ===" -ForegroundColor Cyan
Write-Host "`nThis script will:" -ForegroundColor White
Write-Host "  1. Fix common Beads configuration issues" -ForegroundColor Gray
Write-Host "  2. Configure git remote (if needed)" -ForegroundColor Gray
Write-Host "  3. Synchronize with remote repository" -ForegroundColor Gray
Write-Host "  4. Create beads-sync branch for team collaboration" -ForegroundColor Gray
Write-Host "  5. Set up git hooks and upstream tracking" -ForegroundColor Gray
Write-Host "  6. Perform initial Beads sync" -ForegroundColor Gray
Write-Host "  7. Optionally create an initial git commit" -ForegroundColor Gray
if (-not $YesToAll) {
    Write-Host "`nNote: You'll be asked to confirm before any push to remote repository" -ForegroundColor Yellow
}
Write-Host ""

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
        $hasRemote = $RemoteUrl
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

# Ensure repo has an initial commit before syncing/pushing
$hasCommits = git rev-parse HEAD 2>$null
$workingTreeChanges = git status --porcelain 2>$null
if (-not $hasCommits -and $workingTreeChanges) {
    Write-Host "`nStep 2b: No commits found. An initial commit is required before pushing." -ForegroundColor Yellow
    Write-Host "This will commit all current files with message: 'chore: initial commit'" -ForegroundColor Yellow
    
    $shouldCommit = $YesToAll
    if (-not $YesToAll) {
        $response = Read-Host "Create initial commit now? (y/n)"
        $shouldCommit = $response -eq 'y' -or $response -eq 'Y' -or $response -eq 'yes'
    }
    
    if ($shouldCommit) {
        git add -A 2>&1 | Out-String | Write-Host
        git commit -m "chore: initial commit" 2>&1 | Out-String | Write-Host
        Write-Host "Initial commit created" -ForegroundColor Green
    }
    else {
        Write-Host "Skipped initial commit. You can commit later with: git add -A; git commit -m \"chore: initial commit\"" -ForegroundColor Yellow
    }
}

# Synchronize with remote if it exists and has content
if ($hasRemote -and -not $SkipRemote) {
    Write-Host "`nStep 2a: Synchronizing with remote..." -ForegroundColor Green
    
    # Fetch remote branches
    Write-Host "Fetching from remote..."
    git fetch origin 2>&1 | Out-String | Write-Host
    
    # Check if remote has the current branch
    $remoteBranch = git ls-remote --heads origin $currentBranch 2>$null
    
    if ($remoteBranch) {
        Write-Host "Remote has $currentBranch branch. Checking for divergence..."
        
        # Check if we have local commits
        $hasLocalCommits = git rev-parse HEAD 2>$null
        
        if ($hasLocalCommits) {
            # Check if local and remote have diverged
            $remoteCommits = git rev-list "origin/$currentBranch" --count 2>$null
            $localCommits = git rev-list HEAD --count 2>$null
            
            if ($remoteCommits -and $localCommits) {
                # Both have commits - need to merge
                Write-Host "Both local and remote have commits. Attempting to merge..."
                git merge "origin/$currentBranch" --allow-unrelated-histories -m "chore: merge remote changes" 2>&1 | Out-String | Write-Host
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "WARNING: Merge conflict detected. Please resolve conflicts manually:" -ForegroundColor Yellow
                    Write-Host "  1. Resolve conflicts in the affected files" -ForegroundColor Yellow
                    Write-Host "  2. Run: git add ." -ForegroundColor Yellow
                    Write-Host "  3. Run: git commit -m 'chore: resolve merge conflicts'" -ForegroundColor Yellow
                    Write-Host "  4. Re-run this script" -ForegroundColor Yellow
                    exit 1
                }
                
                Write-Host "Successfully merged remote changes" -ForegroundColor Green
            }
            else {
                Write-Host "Local and remote are in sync" -ForegroundColor Green
            }
        }
        else {
            # No local commits, just pull
            Write-Host "No local commits. Pulling from remote..."
            git pull origin $currentBranch 2>&1 | Out-String | Write-Host
        }
    }
    else {
        Write-Host "Remote does not have $currentBranch branch yet. Will push later." -ForegroundColor Yellow
    }
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
        Write-Host "`nReady to push beads-sync branch to remote" -ForegroundColor Yellow
        Write-Host "Repository: $hasRemote" -ForegroundColor Cyan
        Write-Host "Branch: beads-sync" -ForegroundColor Cyan
        
        $shouldPush = $YesToAll
        if (-not $YesToAll) {
            $response = Read-Host "Push beads-sync branch to remote? (y/n)"
            $shouldPush = $response -eq 'y' -or $response -eq 'Y' -or $response -eq 'yes'
        }
        
        if ($shouldPush) {
            Write-Host "Pushing beads-sync to remote..." -ForegroundColor Green
            git push -u origin beads-sync 2>&1 | Out-String | Write-Host
            Write-Host "✓ beads-sync branch pushed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "Skipped pushing beads-sync branch. You can push later with: git push -u origin beads-sync" -ForegroundColor Yellow
        }
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
            Write-Host "`nReady to push $currentBranch branch to remote" -ForegroundColor Yellow
            Write-Host "Repository: $hasRemote" -ForegroundColor Cyan
            Write-Host "Branch: $currentBranch" -ForegroundColor Cyan
            
            $shouldPush = $YesToAll
            if (-not $YesToAll) {
                $response = Read-Host "Push $currentBranch branch to remote? (y/n)"
                $shouldPush = $response -eq 'y' -or $response -eq 'Y' -or $response -eq 'yes'
            }
            
            if ($shouldPush) {
                Write-Host "Pushing $currentBranch to remote..." -ForegroundColor Green
                git push -u origin $currentBranch 2>&1 | Out-String | Write-Host
                Write-Host "✓ $currentBranch branch pushed successfully" -ForegroundColor Green
            }
            else {
                Write-Host "Skipped pushing $currentBranch branch. You can push later with: git push -u origin $currentBranch" -ForegroundColor Yellow
            }
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
