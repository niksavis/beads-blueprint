#!/usr/bin/env bash
# Team Setup Script for Beads
# Configures the project for team collaboration with beads-sync branch

set -e

REMOTE_URL=""
SKIP_REMOTE=false

show_help() {
    cat << EOF
Team Setup Script for Beads

This script configures your Beads project for team collaboration:
  1. Fixes common Beads configuration issues
  2. Sets up git remote (if needed)
  3. Creates beads-sync branch for issue synchronization
  4. Configures git hooks
  5. Performs initial sync

Usage:
  bash scripts/setup_team.sh                              # Interactive mode
  bash scripts/setup_team.sh --remote-url <url>           # Specify remote URL
  bash scripts/setup_team.sh --skip-remote                # Skip remote setup
  bash scripts/setup_team.sh --help                       # Show this help

Examples:
  bash scripts/setup_team.sh --remote-url "https://github.com/user/repo.git"
  bash scripts/setup_team.sh --skip-remote  # For local-only testing

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remote-url)
            REMOTE_URL="$2"
            shift 2
            ;;
        --skip-remote)
            SKIP_REMOTE=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$(dirname "$0")/.."

echo -e "\n=== Beads Team Setup ==="

# Check if bd is available
if ! command -v bd &> /dev/null; then
    if [ -f "tools/bin/bd" ]; then
        export PATH="$PWD/tools/bin:$PATH"
        echo "Added tools/bin to PATH"
    else
        echo "ERROR: bd command not found. Run bootstrap_beads.sh first."
        exit 1
    fi
fi

# Check if Beads is initialized
if [ ! -f ".beads/beads.db" ]; then
    echo "ERROR: Beads not initialized. Run 'bd init' first."
    exit 1
fi

echo -e "\nStep 1: Running bd doctor --fix..."
bd doctor --fix --yes || true

# Check if git remote exists
HAS_REMOTE=""
if git remote get-url origin &> /dev/null; then
    HAS_REMOTE=$(git remote get-url origin)
fi

if [ -z "$HAS_REMOTE" ] && [ "$SKIP_REMOTE" = false ]; then
    echo -e "\nStep 2: Setting up git remote..."
    
    if [ -z "$REMOTE_URL" ]; then
        echo "No remote configured. Please enter your git remote URL:"
        echo "Example: https://github.com/user/repo.git"
        read -p "Remote URL: " REMOTE_URL
    fi
    
    if [ -n "$REMOTE_URL" ]; then
        echo "Adding remote 'origin': $REMOTE_URL"
        git remote add origin "$REMOTE_URL"
        echo "Remote added successfully"
    else
        echo "Skipping remote setup (you can add it later with: git remote add origin <url>)"
    fi
elif [ -n "$HAS_REMOTE" ]; then
    echo -e "\nStep 2: Git remote already configured: $HAS_REMOTE"
else
    echo -e "\nStep 2: Skipping remote setup (--skip-remote flag)"
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

echo -e "\nStep 3: Checking beads-sync branch..."

# Check if beads-sync branch exists locally
if ! git rev-parse --verify beads-sync &> /dev/null; then
    echo "Creating beads-sync branch..."
    
    # Check if we have commits
    if ! git rev-parse HEAD &> /dev/null; then
        echo "No commits yet. Creating initial commit..."
        git add .beads/issues.jsonl
        git commit -m "chore: initialize beads" --allow-empty
    fi
    
    # Create beads-sync branch
    git checkout -b beads-sync
    echo "beads-sync branch created"
    
    # Push to remote if available
    if [ -n "$HAS_REMOTE" ] && [ "$SKIP_REMOTE" = false ]; then
        echo "Pushing beads-sync to remote..."
        git push -u origin beads-sync || true
    fi
    
    # Return to original branch
    git checkout "$CURRENT_BRANCH"
else
    echo "beads-sync branch already exists"
fi

# Set upstream for current branch if remote exists
if [ -n "$HAS_REMOTE" ] && [ "$SKIP_REMOTE" = false ]; then
    echo -e "\nStep 4: Configuring upstream for $CURRENT_BRANCH..."
    
    if ! git rev-parse --abbrev-ref "$CURRENT_BRANCH@{upstream}" &> /dev/null; then
        # Check if branch exists on remote
        if git ls-remote --heads origin "$CURRENT_BRANCH" &> /dev/null | grep -q "$CURRENT_BRANCH"; then
            echo "Setting upstream to origin/$CURRENT_BRANCH"
            git branch --set-upstream-to=origin/"$CURRENT_BRANCH" "$CURRENT_BRANCH"
        else
            echo "Pushing $CURRENT_BRANCH to remote..."
            git push -u origin "$CURRENT_BRANCH" || true
        fi
        echo "Upstream configured"
    else
        echo "Upstream already configured"
    fi
else
    echo -e "\nStep 4: Skipping upstream configuration (no remote)"
fi

echo -e "\nStep 5: Initial Beads sync..."
bd sync || true

echo -e "\n=== Team Setup Complete ==="
cat << EOF

Your Beads project is now configured for team collaboration!

Next steps:
  1. Team members should clone the repository
  2. Run: bash scripts/bootstrap_beads.sh
  3. Run: bash scripts/setup_team.sh
  4. Start creating issues: bd create "Title" --description "Description" -p 2 -t feature

Workflow:
  - Before starting work: bd sync --import (or git pull)
  - Create/update issues: bd create, bd update, bd close
  - Share changes: bd sync (exports to JSONL and commits)
  - Push to team: git push

Documentation: See agents.md for complete workflow rules.

EOF
