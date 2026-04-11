[CmdletBinding()]
param(
    [string]$ProjectName = $env:PROJECT_NAME,
    [string]$GitName = $env:GIT_NAME,
    [string]$GitEmail = $env:GIT_EMAIL,
    [string]$TemplateUrl = $env:TEMPLATE_URL
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

function Get-GitConfigValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    $value = & git config --get $Key 2>$null
    if ($LASTEXITCODE -eq 0) {
        return $value
    }
    if ($LASTEXITCODE -eq 1) {
        return $null
    }

    throw "git config --get $Key failed with exit code $LASTEXITCODE."
}

function Initialize-Repository {
    & git init -b main
    if ($LASTEXITCODE -eq 0) {
        return
    }

    Invoke-Git -Arguments @("init")
    Invoke-Git -Arguments @("branch", "-M", "main")
}

if (-not $ProjectName) {
    $ProjectName = "my-project"
}
if (-not $TemplateUrl) {
    $TemplateUrl = "https://github.com/niksavis/beads-blueprint.git"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required but was not found in PATH."
}

if (Test-Path -LiteralPath $ProjectName) {
    throw "Target path '$ProjectName' already exists. Choose a different project name."
}

Invoke-Git -Arguments @("clone", "--", $TemplateUrl, $ProjectName)
Set-Location -LiteralPath $ProjectName
Remove-Item -Recurse -Force .git
Initialize-Repository

$shouldCommit = $false
if ($GitName) { Invoke-Git -Arguments @("config", "--local", "user.name", $GitName) }
if ($GitEmail) { Invoke-Git -Arguments @("config", "--local", "user.email", $GitEmail) }

$configuredName = Get-GitConfigValue -Key "user.name"
$configuredEmail = Get-GitConfigValue -Key "user.email"
if ($configuredName -and $configuredEmail) {
    $shouldCommit = $true
}

if ($shouldCommit) {
    Invoke-Git -Arguments @("add", ".")
    Invoke-Git -Arguments @("commit", "-m", "chore: initialize project from template")
}
else {
    Write-Host "Skipped initial commit: git user.name/user.email not configured."
    Write-Host "To set locally for this repo:"
    Write-Host "  git config --local user.name \"John Smith\""
    Write-Host "  git config --local user.email \"john.smith@email.com\""
}

Write-Host ""
Write-Host "Project created: $ProjectName"
Write-Host "Next step: open this folder in VS Code and run Copilot prompt:"
Write-Host "Initialize this repository from scratch. Install and verify all tools, hooks, dependencies, Beads, and Dolt, then tell me what to do next."
