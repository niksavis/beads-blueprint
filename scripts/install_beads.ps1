param(
    [string]$ToolsRoot = "$PSScriptRoot\..\tools",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Detect OS and architecture
$platform = $null
$arch = $null

if ($IsWindows) {
    $platform = "windows"
}
elseif ($IsMacOS) {
    $platform = "darwin"
}
elseif ($IsLinux) {
    $platform = "linux"
}
else {
    throw "Unsupported operating system"
}

# Detect architecture
$archInfo = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
switch ($archInfo) {
    "X64" { $arch = "amd64" }
    "Arm64" { $arch = "arm64" }
    default {
        throw "Unsupported architecture: $archInfo"
    }
}

Write-Host "Detected platform: $platform-$arch" -ForegroundColor Yellow

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
    throw "No asset found for $platform-$arch. Expected: $assetName"
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

Write-Host "Beads installed successfully!" -ForegroundColor Green
Write-Host "Binary: $bdPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use Beads, either:"
Write-Host "  1. Add $binDir to PATH"
Write-Host "  2. Or invoke directly: & $bdPath --version"
