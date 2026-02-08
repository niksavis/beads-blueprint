#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_ROOT="${1:-$SCRIPT_DIR/../tools}"
BIN_DIR="$TOOLS_ROOT/bin"

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)

case "$OS" in
    Darwin)
        PLATFORM="darwin"
        ;;
    Linux)
        PLATFORM="linux"
        ;;
    FreeBSD)
        PLATFORM="freebsd"
        ;;
    *)
        echo "Unsupported operating system: $OS" >&2
        echo "Beads supports: Linux, macOS (Darwin), FreeBSD" >&2
        echo "" >&2
        echo "To build from source for your platform:" >&2
        echo "  https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" >&2
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64)
        ARCH_NAME="amd64"
        ;;
    aarch64|arm64)
        ARCH_NAME="arm64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH" >&2
        echo "Beads supports: amd64 (x86_64), arm64 (aarch64)" >&2
        echo "" >&2
        echo "To build from source for your platform:" >&2
        echo "  https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" >&2
        exit 1
        ;;
esac

echo "Detected platform: $PLATFORM-$ARCH_NAME"

# Fetch latest release
API_URL="https://api.github.com/repos/steveyegge/beads/releases/latest"
echo "Fetching latest release..."
JSON=$(curl -sSL -H "Accept: application/vnd.github+json" "$API_URL")

# Extract version (remove 'v' prefix)
VERSION=$(echo "$JSON" | python3 -c "import sys, json; v = json.load(sys.stdin)['tag_name']; print(v[1:] if v.startswith('v') else v)")
echo "Latest version: $VERSION"

# Determine archive extension and asset name
if [ "$PLATFORM" = "windows" ]; then
    EXTENSION="zip"
else
    EXTENSION="tar.gz"
fi

ASSET_NAME="beads_${VERSION}_${PLATFORM}_${ARCH_NAME}.${EXTENSION}"
echo "Looking for asset: $ASSET_NAME"

#Find specific asset
ASSET_URL=$(echo "$JSON" | python3 -c "
import sys, json
release = json.load(sys.stdin)
asset_name = '$ASSET_NAME'
for a in release.get('assets', []):
    if a.get('name') == asset_name:
        print(a['browser_download_url'])
        break
")

if [ -z "$ASSET_URL" ]; then
  echo "No prebuilt binary found for $PLATFORM-$ARCH_NAME" >&2
  echo "Expected asset: $ASSET_NAME" >&2
  echo "" >&2
  echo "Beads supports:" >&2
  echo "  - macOS (darwin): amd64, arm64" >&2
  echo "  - Linux: amd64, arm64" >&2
  echo "  - FreeBSD: amd64" >&2
  echo "  - Android: arm64" >&2
  echo "" >&2
  echo "To build from source for your platform:" >&2
  echo "  https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md" >&2
  exit 1
fi

TMP_ARCHIVE="${TMPDIR:-/tmp}/beads-latest.$EXTENSION"
mkdir -p "$BIN_DIR"

echo "Downloading from $ASSET_URL..."
curl -sSL "$ASSET_URL" -o "$TMP_ARCHIVE"

echo "Extracting to $BIN_DIR..."
if [ "$EXTENSION" = "zip" ]; then
    unzip -o "$TMP_ARCHIVE" -d "$BIN_DIR" >/dev/null
else
    tar -xzf "$TMP_ARCHIVE" -C "$BIN_DIR"
fi

# Verify bd executable exists
BD_PATH="$BIN_DIR/bd"
if [ ! -f "$BD_PATH" ]; then
  echo "Could not find bd executable at $BD_PATH after extraction" >&2
  exit 1
fi

# Make executable
chmod +x "$BD_PATH"

echo "Beads installed successfully!"
echo "Binary: $BD_PATH"
echo ""
echo "To use Beads, either:"
echo "  1. Add $BIN_DIR to PATH"
echo "  2. Or invoke directly: $BD_PATH --version"
