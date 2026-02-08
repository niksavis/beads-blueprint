"""Generate changelog draft from git commits for LLM processing.

Workflow:
1. Run: python regenerate_changelog.py --preview --json
2. Creates changelog_draft.json with unreleased commits since last tag
3. Use LLM/Agent to read JSON and write polished changelog section
4. Copy LLM output to changelog.md as ## vX.Y.Z section
5. Run: python release.py [patch|minor|major]

Alternative (manual TBD placeholders):
- python regenerate_changelog.py --version 0.2.0
- Scaffolds empty section with TBD placeholders
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
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


def extract_beads_issue(commit_msg: str) -> str | None:
    """Extract Beads issue ID from commit message (e.g., 'beads-blueprint-abc')."""
    # Match both formats: (bd-xxx) and "Closes beads-blueprint-xxx"
    patterns = [
        r"\(bd-([a-z0-9]+)\)",
        r"Closes\s+beads-blueprint-([a-z0-9]+)",
    ]
    for pattern in patterns:
        if match := re.search(pattern, commit_msg, re.IGNORECASE):
            return match.group(1).lower()
    return None


def get_beads_issue_title(issue_id: str) -> str | None:
    """Fetch issue title from .beads/issues.jsonl."""
    issues_file = Path(".beads/issues.jsonl")
    if not issues_file.exists():
        return None

    full_id = f"beads-blueprint-{issue_id}"
    try:
        for line in issues_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            issue = json.loads(line)
            if issue.get("id") == full_id:
                return issue.get("title", "")
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def categorize_commit(commit_msg: str) -> tuple[str, str]:
    """Categorize commit and return (category, clean_message)."""
    commit_lower = commit_msg.lower()

    # Try conventional commits format
    if match := re.match(
        r"^(feat|fix|docs|refactor|perf|test|chore|style|build|ci)(\([^)]+\))?:\s*(.+)$",
        commit_msg,
    ):
        commit_type = match.group(1)
        clean_msg = match.group(3).strip()

        type_map = {
            "feat": "Features",
            "fix": "Bug Fixes",
            "docs": "Documentation",
            "perf": "Performance",
            "refactor": "Code Quality",
        }
        return (type_map.get(commit_type, "Other"), clean_msg)

    # Fallback heuristics
    if any(
        word in commit_lower for word in ["add", "implement", "create", "introduce"]
    ):
        return ("Features", commit_msg)
    if any(word in commit_lower for word in ["fix", "resolve", "correct", "patch"]):
        return ("Bug Fixes", commit_msg)

    return ("Other", commit_msg)


def group_commits(commits: list[str]) -> dict[str, list[str]]:
    """Group commits by Beads issue or category."""
    grouped = defaultdict(list)

    for commit in commits:
        # Check for Beads issue
        issue_id = extract_beads_issue(commit)
        if issue_id:
            issue_title = get_beads_issue_title(issue_id) or f"Issue {issue_id}"
            grouped[f"beads:{issue_id}"].append((issue_title, commit))
        else:
            # Group by category
            category, clean_msg = categorize_commit(commit)
            grouped[category].append((clean_msg, commit))

    return dict(grouped)


def generate_draft_json(preview: bool = False) -> None:
    """Generate changelog_draft.json from unreleased commits."""
    try:
        # Get latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        latest_tag = result.stdout.strip()
    except subprocess.CalledProcessError:
        latest_tag = None

    # Get commits since last tag (or all commits if no tags)
    if latest_tag:
        range_spec = f"{latest_tag}..HEAD"
    else:
        range_spec = "HEAD"

    try:
        commits_result = subprocess.run(
            ["git", "log", range_spec, "--pretty=format:%s", "--no-merges"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = [c for c in commits_result.stdout.strip().split("\n") if c]
    except subprocess.CalledProcessError:
        commits = []

    if not commits:
        print(f"✓ No unreleased commits since {latest_tag or 'beginning'}")
        return

    # Group commits
    grouped = group_commits(commits)

    # Build draft data
    draft_data = {
        "version": "vX.Y.Z (UNRELEASED)" if preview else read_version(),
        "date": date.today().isoformat(),
        "since_tag": latest_tag or "initial commit",
        "commit_count": len(commits),
        "commits": commits,
        "grouped": {},
    }

    # Organize by category
    categories = [
        "Features",
        "Bug Fixes",
        "Documentation",
        "Performance",
        "Code Quality",
        "Other",
    ]
    for category in categories:
        if category in grouped:
            draft_data["grouped"][category] = [item[0] for item in grouped[category]]

    # Add Beads issues separately
    beads_issues = {k: v for k, v in grouped.items() if k.startswith("beads:")}
    if beads_issues:
        draft_data["beads_issues"] = {
            issue_id.replace("beads:", ""): items[0][0]
            for issue_id, items in beads_issues.items()
        }

    # Write to file
    json_path = Path("changelog_draft.json")
    json_path.write_text(json.dumps(draft_data, indent=2), encoding="utf-8")

    print(f"✓ Generated {json_path} with {len(commits)} commits")
    print(f"  Since: {latest_tag or 'beginning'}")
    print()
    print("📝 Next steps:")
    print("  1. Ask LLM/Agent to read changelog_draft.json")
    print("  2. LLM writes user-friendly changelog section")
    print("  3. Copy to changelog.md as ## vX.Y.Z section")
    print("  4. Run: python release.py [patch|minor|major]")


def build_section(version_str: str, release_date: str) -> str:
    """Build placeholder changelog section."""
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
    """Add placeholder section to changelog (called by release.py)."""
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
    parser = argparse.ArgumentParser(
        description="Generate changelog draft or scaffold placeholder"
    )
    parser.add_argument("--version", help="Version without leading v")
    parser.add_argument("--date", help="Release date in YYYY-MM-DD format")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview unreleased commits since last tag",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export to changelog_draft.json for LLM processing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # JSON draft mode (for LLM processing)
    if args.json:
        generate_draft_json(preview=args.preview)
        return 0

    # Preview mode (print to console)
    if args.preview:
        print("Use --json flag to generate changelog_draft.json")
        return 0

    # Manual placeholder mode (called by release.py or standalone)
    version_str = args.version or read_version()
    release_date = args.date or date.today().isoformat()
    ensure_version_section(version_str, release_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
