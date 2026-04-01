#!/usr/bin/env python3
"""Configure Git merge settings for Beads JSONL files."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_git_config(repo_root: Path, key: str, value: str) -> None:
    subprocess.run(
        ["git", "config", key, value],
        cwd=repo_root,
        check=True,
    )


def configure_merge_driver(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        print("Skipping Git configuration: no .git directory found.")
        return

    run_git_config(repo_root, "merge.beads.name", "Beads JSONL merge")
    run_git_config(repo_root, "merge.beads.driver", "bd merge %A %O %B %A --debug")
    print("Configured git merge driver for .beads/issues.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Beads Git integration")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    configure_merge_driver(repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
