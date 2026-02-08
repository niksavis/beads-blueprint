#!/usr/bin/env python3
"""Minimal release helper for the Beads template.

Usage:
    python release.py patch
    python release.py minor
    python release.py major
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VERSION_FILE = PROJECT_ROOT / "version.py"
README_FILE = PROJECT_ROOT / "readme.md"


def read_version() -> tuple[int, int, int]:
    content = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in version.py")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current: tuple[int, int, int], bump_type: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if bump_type == "major":
        return major + 1, 0, 0
    if bump_type == "minor":
        return major, minor + 1, 0
    if bump_type == "patch":
        return major, minor, patch + 1
    raise ValueError(f"Invalid bump type: {bump_type}")


def write_version(version: tuple[int, int, int]) -> str:
    version_str = f"{version[0]}.{version[1]}.{version[2]}"
    content = VERSION_FILE.read_text(encoding="utf-8")
    updated = re.sub(
        r'(__version__\s*=\s*["\'])\d+\.\d+\.\d+(["\'])',
        rf"\g<1>{version_str}\g<2>",
        content,
    )
    VERSION_FILE.write_text(updated, encoding="utf-8")
    return version_str


def update_readme(version_str: str) -> None:
    content = README_FILE.read_text(encoding="utf-8")
    updated = re.sub(
        r"(\*\*Version:\*\* )\d+\.\d+\.\d+",
        rf"\g<1>{version_str}",
        content,
    )
    README_FILE.write_text(updated, encoding="utf-8")


def update_changelog(version_str: str) -> None:
    from regenerate_changelog import ensure_version_section

    ensure_version_section(version_str, date.today().isoformat())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump version for the template")
    parser.add_argument("bump", choices=["major", "minor", "patch"])
    parser.add_argument(
        "--skip-changelog",
        action="store_true",
        help="Do not modify changelog.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = read_version()
    next_version = bump_version(current, args.bump)
    version_str = write_version(next_version)
    update_readme(version_str)
    if not args.skip_changelog:
        update_changelog(version_str)
    print(f"Updated version to {version_str}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
