"""Convert a plan markdown file into Beads CLI commands."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
            title = line.split("- Subtask:", 1)[1].strip()
            title, priority = parse_priority(title)
            parent_title = current_task.title if current_task else ""
            subtask = PlanItem("subtask", title, parent_title, priority, [])
            items.append(subtask)
            continue

        if line.lstrip().startswith("- Notes:"):
            note = line.split("- Notes:", 1)[1].strip()
            if current_task:
                current_task.notes.append(note)
            elif current_feature:
                current_feature.notes.append(note)

    return items


def ps_quote(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def build_description(item: PlanItem, plan_path: Path) -> str:
    parts = [f"Plan: {plan_path.name}"]
    if item.parent_title:
        parts.append(f"Parent: {item.parent_title}")
    if item.notes:
        parts.append("Notes: " + "; ".join(item.notes))
    return ". ".join(parts)


def build_command(item: PlanItem, plan_path: Path) -> str:
    description = build_description(item, plan_path)
    return (
        f"bd create {ps_quote(item.title)} "
        f"--description {ps_quote(description)} "
        f"-p {item.priority} -t {item.item_type} --json"
    )


def write_commands(
    items: list[PlanItem], plan_path: Path, output_path: Path | None
) -> None:
    commands = [build_command(item, plan_path) for item in items]
    if output_path:
        content = "\n".join(commands) + "\n"
        output_path.write_text(content, encoding="utf-8")
        print(f"Wrote {len(commands)} commands to {output_path}")
    else:
        for command in commands:
            print(command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert plan markdown to Beads commands"
    )
    parser.add_argument("--plan", default="templates/plan_template.md")
    parser.add_argument("--output", help="Write commands to a .ps1 file")
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

    output_path = Path(args.output) if args.output else None
    write_commands(items, plan_path, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
