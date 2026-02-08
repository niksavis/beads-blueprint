#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_ROOT="${1:-$SCRIPT_ROOT/../tools}"
SKIP_INSTALL="${2:-}"

if [ "$SKIP_INSTALL" != "--skip-install" ]; then
  # Check if bd is already available
  if command -v bd >/dev/null 2>&1; then
    echo ""
    echo "Beads (bd) is already available in PATH."
    
    # Check if running interactively
    if [ -t 0 ]; then
      read -p "Skip local installation? (Y/n) " -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        SKIP_INSTALL="--skip-install"
        echo "Using system Beads installation."
      fi
    else
      # Non-interactive (piped), default to installing locally
      echo "Non-interactive mode: Installing locally to ensure project has its own copy."
      echo ""
    fi
  fi
fi

if [ "$SKIP_INSTALL" != "--skip-install" ]; then
  "$SCRIPT_ROOT/install_beads.sh" "$TOOLS_ROOT"
  
  # Configure VS Code workspace settings
  echo ""
  echo "=== Configuring VS Code ==="
  
  REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"
  VSCODE_DIR="$REPO_ROOT/.vscode"
  SETTINGS_FILE="$VSCODE_DIR/settings.json"
  
  mkdir -p "$VSCODE_DIR"
  
  if [ -f "$SETTINGS_FILE" ]; then
    # Check if PATH configuration already exists
    if grep -q "terminal.integrated.env.windows" "$SETTINGS_FILE" 2>/dev/null; then
      echo "Terminal PATH configuration already exists in workspace settings"
    else
      echo "Note: Workspace settings exist. Please manually add:"
      echo '  "terminal.integrated.env.windows": {'
      echo '    "PATH": "${env:PATH};${workspaceFolder}\\tools\\bin"'
      echo '  }'
    fi
  else
    # Create new settings file
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "terminal.integrated.env.windows": {
    "PATH": "${env:PATH};${workspaceFolder}\\tools\\bin"
  }
}
EOF
    echo "Created workspace settings with terminal PATH configuration"
    echo "VS Code Beads extension will now find the local daemon"
  fi
fi

"$SCRIPT_ROOT/configure_beads.sh"

if [ "$SKIP_INSTALL" != "--skip-install" ]; then
  BIN_DIR="$TOOLS_ROOT/bin"
  BD_PATH="$BIN_DIR/bd"

  if [ -f "$BD_PATH" ]; then
    echo ""
    echo "Verification:"
    "$BD_PATH" --version
  else
    echo "Beads installed, but binary not found at expected location." >&2
  fi
else
  echo ""
  echo "Verification:"
  bd --version
fi