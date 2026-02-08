"""Changelog scaffolding for the Beads template."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
CHANGELOG_FILE = PROJECT_ROOT / "changelog.md"
VERSION_FILE = PROJECT_ROOT / "version.py"


def read_version() -> str:
    content = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in version.py")
    return match.group(1)


def build_section(version_str: str, release_date: str) -> str:
    return (
        f"## v{version_str}\n\n"
        f"*Released: {release_date}*\n\n"
        "### Features\n\n"
        "- TBD\n\n"
        "### Improvements\n\n"
        "- TBD\n\n"
        "### Bug Fixes\n\n"
        "- TBD\n\n"
    )


def ensure_version_section(version_str: str, release_date: str) -> None:
    if not CHANGELOG_FILE.exists():
        CHANGELOG_FILE.write_text("# Changelog\n\n", encoding="utf-8")

    content = CHANGELOG_FILE.read_text(encoding="utf-8")
    if re.search(rf"^## v{re.escape(version_str)}\b", content, re.MULTILINE):
        print(f"Changelog already has v{version_str}")
        return

    lines = content.splitlines(keepends=True)
    if lines and lines[0].strip() == "# Changelog":
        insert_at = 1
    else:
        lines.insert(0, "# Changelog\n")
        lines.insert(1, "\n")
        insert_at = 2

    section = build_section(version_str, release_date)
    lines.insert(insert_at, section)
    CHANGELOG_FILE.write_text("".join(lines), encoding="utf-8")
    print(f"Added changelog section for v{version_str}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a changelog section")
    parser.add_argument("--version", help="Version without leading v")
    parser.add_argument("--date", help="Release date in YYYY-MM-DD format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version_str = args.version or read_version()
    release_date = args.date or date.today().isoformat()
    ensure_version_section(version_str, release_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
