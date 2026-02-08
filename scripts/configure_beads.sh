#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
cd "$REPO_ROOT"

git config merge.beads.name "Beads JSONL merge"
git config merge.beads.driver "bd merge %A %O %B %A --debug"

echo "Configured git merge driver for .beads/issues.jsonl"