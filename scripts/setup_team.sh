#!/usr/bin/env bash
# Team Setup Script for Beads
# Configures the project for team collaboration with beads-sync branch

set -e

REMOTE_URL=""
SKIP_REMOTE=false
YES_TO_ALL=false

show_help() {
    cat << EOF
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
  bash scripts/setup_team.sh                              # Interactive mode
  bash scripts/setup_team.sh --remote-url <url>           # Specify remote URL
  bash scripts/setup_team.sh --skip-remote                # Skip remote setup
  bash scripts/setup_team.sh --yes-to-all                 # Skip all confirmations
  bash scripts/setup_team.sh --help                       # Show this help

Examples:
  bash scripts/setup_team.sh --remote-url "https://github.com/user/repo.git"
  bash scripts/setup_team.sh --skip-remote  # For local-only testing

Notes:
  - If remote repository was initialized with files (README, etc.),
    the script will automatically merge with --allow-unrelated-histories
  - If merge conflicts occur, you'll be prompted to resolve them manually

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
        --yes-to-all)
            YES_TO_ALL=true
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
echo -e "\nThis script will:"
echo -e "  1. Fix common Beads configuration issues"
echo -e "  2. Configure git remote (if needed)"
echo -e "  3. Synchronize with remote repository"
echo -e "  4. Create beads-sync branch for team collaboration"
echo -e "  5. Set up git hooks and upstream tracking"
echo -e "  6. Perform initial Beads sync"
echo -e "  7. Optionally create an initial git commit"
if [ "$YES_TO_ALL" != true ]; then
    echo -e "\nNote: You'll be asked to confirm before any push to remote repository"
fi
echo ""

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
        HAS_REMOTE="$REMOTE_URL"
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

# Ensure repo has an initial commit before syncing/pushing
if ! git rev-parse HEAD &> /dev/null; then
    WORKING_TREE_CHANGES=$(git status --porcelain 2>/dev/null || true)
    if [ -n "$WORKING_TREE_CHANGES" ]; then
        echo -e "\nStep 2b: No commits found. An initial commit is required before pushing."
        echo -e "This will commit all current files with message: 'chore: initial commit'"
        
        SHOULD_COMMIT=false
        if [ "$YES_TO_ALL" = true ]; then
            SHOULD_COMMIT=true
        else
            read -p "Create initial commit now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                SHOULD_COMMIT=true
            fi
        fi
        
        if [ "$SHOULD_COMMIT" = true ]; then
            git add -A 2>&1 || true
            git commit -m "chore: initial commit" 2>&1 || true
            echo "Initial commit created"
        else
            echo "Skipped initial commit. You can commit later with: git add -A; git commit -m \"chore: initial commit\""
        fi
    fi
fi

# Synchronize with remote if it exists and has content
if [ -n "$HAS_REMOTE" ] && [ "$SKIP_REMOTE" = false ]; then
    echo -e "\nStep 2a: Synchronizing with remote..."
    
    # Fetch remote branches
    echo "Fetching from remote..."
    git fetch origin 2>&1 || true
    
    # Check if remote has the current branch
    if git ls-remote --heads origin "$CURRENT_BRANCH" 2>/dev/null | grep -q "$CURRENT_BRANCH"; then
        echo "Remote has $CURRENT_BRANCH branch. Checking for divergence..."
        
        # Check if we have local commits
        if git rev-parse HEAD &> /dev/null; then
            # Check if local and remote have diverged
            REMOTE_COMMITS=$(git rev-list "origin/$CURRENT_BRANCH" --count 2>/dev/null || echo "0")
            LOCAL_COMMITS=$(git rev-list HEAD --count 2>/dev/null || echo "0")
            
            if [ "$REMOTE_COMMITS" -gt 0 ] && [ "$LOCAL_COMMITS" -gt 0 ]; then
                # Both have commits - need to merge
                echo "Both local and remote have commits. Attempting to merge..."
                if ! git merge "origin/$CURRENT_BRANCH" --allow-unrelated-histories -m "chore: merge remote changes" 2>&1; then
                    echo "WARNING: Merge conflict detected. Please resolve conflicts manually:"
                    echo "  1. Resolve conflicts in the affected files"
                    echo "  2. Run: git add ."
                    echo "  3. Run: git commit -m 'chore: resolve merge conflicts'"
                    echo "  4. Re-run this script"
                    exit 1
                fi
                
                echo "Successfully merged remote changes"
            else
                echo "Local and remote are in sync"
            fi
        else
            # No local commits, just pull
            echo "No local commits. Pulling from remote..."
            git pull origin "$CURRENT_BRANCH" 2>&1 || true
        fi
    else
        echo "Remote does not have $CURRENT_BRANCH branch yet. Will push later."
    fi
fi

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
        echo -e "\nReady to push beads-sync branch to remote"
        echo -e "Repository: $HAS_REMOTE"
        echo -e "Branch: beads-sync"
        
        SHOULD_PUSH=false
        if [ "$YES_TO_ALL" = true ]; then
            SHOULD_PUSH=true
        else
            read -p "Push beads-sync branch to remote? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                SHOULD_PUSH=true
            fi
        fi
        
        if [ "$SHOULD_PUSH" = true ]; then
            echo "Pushing beads-sync to remote..."
            git push -u origin beads-sync || true
            echo "✓ beads-sync branch pushed successfully"
        else
            echo "Skipped pushing beads-sync branch. You can push later with: git push -u origin beads-sync"
        fi
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
            echo -e "\nReady to push $CURRENT_BRANCH branch to remote"
            echo -e "Repository: $HAS_REMOTE"
            echo -e "Branch: $CURRENT_BRANCH"
            
            SHOULD_PUSH=false
            if [ "$YES_TO_ALL" = true ]; then
                SHOULD_PUSH=true
            else
                read -p "Push $CURRENT_BRANCH branch to remote? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    SHOULD_PUSH=true
                fi
            fi
            
            if [ "$SHOULD_PUSH" = true ]; then
                echo "Pushing $CURRENT_BRANCH to remote..."
                git push -u origin "$CURRENT_BRANCH" || true
                echo "✓ $CURRENT_BRANCH branch pushed successfully"
            else
                echo "Skipped pushing $CURRENT_BRANCH branch. You can push later with: git push -u origin $CURRENT_BRANCH"
            fi
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
