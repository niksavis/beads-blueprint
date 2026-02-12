#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
cd "$REPO_ROOT"

if [ ! -d "$REPO_ROOT/.git" ]; then
	echo "Warning: Not a git repository. Skipping git merge driver configuration."
	exit 0
fi

git config merge.beads.name "Beads JSONL merge"
git config merge.beads.driver "bd merge %A %O %B %A --debug"

echo "Configured git merge driver for .beads/issues.jsonl"