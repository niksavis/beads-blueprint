#!/usr/bin/env bash
set -euo pipefail

TEMPLATE_URL="${TEMPLATE_URL:-https://github.com/niksavis/beads-blueprint.git}"
PROJECT_NAME="${PROJECT_NAME:-my-project}"
GIT_NAME="${GIT_NAME:-}"
GIT_EMAIL="${GIT_EMAIL:-}"

usage() {
  cat <<'EOF'
Usage: new-project.sh [--project-name <name>] [--git-name <name>] [--git-email <email>]

Environment variables (works with curl | bash):
  PROJECT_NAME
  GIT_NAME
  GIT_EMAIL
  TEMPLATE_URL

Options:
  --project-name   Local project folder name (default: my-project)
  --git-name       Local git user.name for this repo only
  --git-email      Local git user.email for this repo only
  -h, --help       Show this help message
EOF
}

init_repo_main_branch() {
  # Support both modern and older Git versions.
  if git init -b main >/dev/null 2>&1; then
    return 0
  fi

  git init
  git branch -M main
}

sanitize_template_artifacts() {
  # Remove template-only wrappers, release artifacts, and infrastructure
  # tests from generated projects. Users start with a clean baseline.
  rm -f \
    "scripts/new-project.sh" \
    "scripts/new-project.ps1" \
    "changelog.md" \
    "version.py"
  find tests/ -maxdepth 1 -name '*.py' ! -name '__init__.py' ! -name 'test_smoke.py' -delete
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-name)
      [[ $# -ge 2 ]] || { echo "Missing value for --project-name" >&2; exit 1; }
      PROJECT_NAME="$2"
      shift 2
      ;;
    --git-name)
      [[ $# -ge 2 ]] || { echo "Missing value for --git-name" >&2; exit 1; }
      GIT_NAME="$2"
      shift 2
      ;;
    --git-email)
      [[ $# -ge 2 ]] || { echo "Missing value for --git-email" >&2; exit 1; }
      GIT_EMAIL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found in PATH." >&2
  exit 1
fi

if [[ -e "$PROJECT_NAME" ]]; then
  echo "Target path '$PROJECT_NAME' already exists. Choose a different project name." >&2
  exit 1
fi

git clone -- "$TEMPLATE_URL" "$PROJECT_NAME"
cd "$PROJECT_NAME"
rm -rf .git
init_repo_main_branch
sanitize_template_artifacts

should_commit=false
[[ -n "$GIT_NAME" ]] && git config --local user.name "$GIT_NAME"
[[ -n "$GIT_EMAIL" ]] && git config --local user.email "$GIT_EMAIL"

if git config --get user.name >/dev/null 2>&1 && git config --get user.email >/dev/null 2>&1; then
  should_commit=true
fi

if [[ "$should_commit" == true ]]; then
  git add .
  git commit -m "chore: initialize project from template"
else
  echo "Skipped initial commit: git user.name/user.email not configured."
  echo "To set locally for this repo:"
  echo "  git config --local user.name \"John Smith\""
  echo "  git config --local user.email \"john.smith@email.com\""
fi

echo

echo "Project created: $PROJECT_NAME"
echo "Next step: open this folder in VS Code and run Copilot prompt:"
echo "Initialize this repository from scratch. Install and verify all tools, hooks, dependencies, Beads, and Dolt, then tell me what to do next."
