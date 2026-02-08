param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

Set-Location $RepoRoot

git config merge.beads.name "Beads JSONL merge"
git config merge.beads.driver "bd merge %A %O %B %A --debug"

Write-Host "Configured git merge driver for .beads/issues.jsonl"