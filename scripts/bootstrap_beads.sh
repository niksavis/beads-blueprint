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

  TASKS_FILE="$VSCODE_DIR/tasks.json"
  if [ -f "$TASKS_FILE" ]; then
    if grep -q '"label": "Start Beads Daemon with Auto-Sync"' "$TASKS_FILE" 2>/dev/null; then
      echo "Beads daemon task already exists in tasks.json"
    else
      echo "Note: tasks.json exists. Please add the Beads daemon task manually."
    fi
  else
    cat > "$TASKS_FILE" << 'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Beads Daemon with Auto-Sync",
      "type": "shell",
      "command": "${workspaceFolder}/tools/bin/bd",
      "args": ["daemon", "start", "--auto-commit"],
      "isBackground": true,
      "problemMatcher": [],
      "presentation": {
        "echo": false,
        "reveal": "never",
        "focus": false,
        "panel": "shared",
        "showReuseMessage": false,
        "clear": false
      },
      "runOptions": {
        "runOn": "folderOpen"
      }
    }
  ]
}
EOF
    echo "Created tasks.json to start the Beads daemon on folder open"
  fi
fi

SKIP_GIT_CONFIG=false
REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"
if [ ! -d "$REPO_ROOT/.git" ]; then
  if [ -t 0 ]; then
    read -p "No .git found. Initialize a git repository here? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      (cd "$REPO_ROOT" && git init)
    else
      SKIP_GIT_CONFIG=true
    fi
  else
    SKIP_GIT_CONFIG=true
  fi

  if [ "$SKIP_GIT_CONFIG" = true ]; then
    echo "Warning: Not a git repository. Skipping git merge driver configuration."
    echo "Missing features until git is initialized:"
    echo "- Git merge driver for .beads/issues.jsonl"
    echo "- Repository and clone IDs during bd init"
    echo "- Team setup and sync workflows"
    echo "To enable later: run 'git init', then rerun bootstrap_beads.sh or configure_beads.sh."
  fi
fi

if [ "$SKIP_GIT_CONFIG" != true ]; then
  "$SCRIPT_ROOT/configure_beads.sh"
fi

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

echo ""
echo "Bootstrap complete!"