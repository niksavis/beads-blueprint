param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

Set-Location $RepoRoot

$gitDir = Join-Path $RepoRoot ".git"
if (-not (Test-Path $gitDir)) {
    Write-Host "Warning: Not a git repository. Skipping git merge driver configuration." -ForegroundColor Yellow
    exit 0
}

git config merge.beads.name "Beads JSONL merge"
git config merge.beads.driver "bd merge %A %O %B %A --debug"

Write-Host "Configured git merge driver for .beads/issues.jsonl"