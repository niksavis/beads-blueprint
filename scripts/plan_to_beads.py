"""Convert a plan markdown file into Beads JSONL format."""

from __future__ import annotations

import argparse
import json
import secrets
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class PlanItem:
    item_type: str
    title: str
    parent_title: str | None
    priority: int
    notes: list[str]


def parse_priority(text: str) -> tuple[str, int]:
    priority = 2
    title = text
    if "[P" in text and text.endswith("]"):
        head, _, tail = text.rpartition("[P")
        if tail.endswith("]"):
            value = tail.rstrip("]")
            if value.isdigit():
                priority = int(value)
                title = head.strip()
    return title.strip(), priority


def parse_plan(lines: Iterable[str]) -> list[PlanItem]:
    items: list[PlanItem] = []
    current_feature: PlanItem | None = None
    current_task: PlanItem | None = None

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("### Feature:"):
            title = line.replace("### Feature:", "", 1).strip()
            title, priority = parse_priority(title)
            current_feature = PlanItem("feature", title, None, priority, [])
            current_task = None
            items.append(current_feature)
            continue

        if line.lstrip().startswith("- Task:"):
            title = line.split("- Task:", 1)[1].strip()
            title, priority = parse_priority(title)
            parent_title = current_feature.title if current_feature else ""
            current_task = PlanItem("task", title, parent_title, priority, [])
            items.append(current_task)
            continue

        if line.lstrip().startswith("- Subtask:"):
            # Beads doesn't support subtask type, convert to task
            title = line.split("- Subtask:", 1)[1].strip()
            title, priority = parse_priority(title)
            parent_title = current_task.title if current_task else ""
            subtask = PlanItem("task", title, parent_title, priority, [])
            items.append(subtask)
            continue

        if line.lstrip().startswith("- Notes:"):
            note = line.split("- Notes:", 1)[1].strip()
            if current_task:
                current_task.notes.append(note)
            elif current_feature:
                current_feature.notes.append(note)

    return items


def get_prefix() -> str:
    """Get the Beads issue prefix from config or use default."""
    try:
        result = subprocess.run(
            ["bd", "config", "get", "issue.prefix"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            prefix = result.stdout.strip()
            # Handle "issue.prefix (not set)" message from bd
            if "(not set)" not in prefix and prefix:
                return prefix
    except FileNotFoundError:
        pass
    return "beads-blueprint"


def get_git_user() -> tuple[str, str]:
    """Get git user name and email, with fallbacks."""
    try:
        name_result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        email_result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=False,
        )
        name = name_result.stdout.strip() if name_result.returncode == 0 else "User"
        email = (
            email_result.stdout.strip()
            if email_result.returncode == 0
            else "user@example.com"
        )
        return name, email
    except FileNotFoundError:
        return "User", "user@example.com"


def generate_id(prefix: str) -> str:
    """Generate a random Beads issue ID."""
    # Generate 3 random characters (alphanumeric lowercase)
    suffix = "".join(
        secrets.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(3)
    )
    return f"{prefix}-{suffix}"


def build_description(item: PlanItem, plan_path: Path) -> str:
    parts = [f"Plan: {plan_path.name}"]
    if item.parent_title:
        parts.append(f"Parent: {item.parent_title}")
    if item.notes:
        parts.append("Notes: " + "; ".join(item.notes))
    return ". ".join(parts)


def build_issue_json(
    item: PlanItem, plan_path: Path, prefix: str, owner: str, created_by: str
) -> dict:
    """Build a Beads issue as a JSON object."""
    now = datetime.now(timezone.utc).astimezone().isoformat()
    return {
        "id": generate_id(prefix),
        "title": item.title,
        "description": build_description(item, plan_path),
        "status": "open",
        "priority": item.priority,
        "issue_type": item.item_type,
        "owner": owner,
        "created_at": now,
        "created_by": created_by,
        "updated_at": now,
    }


def write_jsonl(
    items: list[PlanItem],
    plan_path: Path,
    output_path: Path,
    prefix: str,
    owner: str,
    created_by: str,
) -> None:
    """Write plan items as JSONL."""
    issues = [
        build_issue_json(item, plan_path, prefix, owner, created_by) for item in items
    ]
    with output_path.open("w", encoding="utf-8") as f:
        for issue in issues:
            f.write(json.dumps(issue, ensure_ascii=False) + "\n")
    print(f"✓ Generated {len(issues)} issues in {output_path}")
    print("  Import with: bd sync --import")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert plan markdown to Beads JSONL format"
    )
    parser.add_argument(
        "--plan",
        default="templates/plan_template.md",
        help="Path to plan markdown file",
    )
    parser.add_argument(
        "--output", default="plan_issues.jsonl", help="Output JSONL file path"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan)
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    items = parse_plan(plan_path.read_text(encoding="utf-8").splitlines())
    if not items:
        print("No plan items found. Check the template format.")
        return 1

    prefix = get_prefix()
    created_by, owner = get_git_user()
    output_path = Path(args.output)

    write_jsonl(items, plan_path, output_path, prefix, owner, created_by)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
