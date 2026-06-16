#!/usr/bin/env python3
"""Deterministic verifier for customization harness integrity."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ARTIFACTS = (
    Path(".github/agents/work-orchestrator.agent.md"),
    Path(".github/skills/orchestrated-execution/SKILL.md"),
    Path(".github/skills/deterministic-quality-gates/SKILL.md"),
    Path(".github/prompts/autonomous-orchestrated-delivery.prompt.md"),
    Path(".github/instructions/orchestration.instructions.md"),
)

INVENTORY_DOCS = (
    Path(".github/copilot_customization.md"),
    Path(".github/copilot_capability_map.md"),
)


@dataclass
class Finding:
    code: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {"code": self.code, "message": self.message}
        if self.path:
            payload["path"] = self.path
        return payload


def parse_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, flags=re.DOTALL)
    if not match:
        if content.startswith("---"):
            raise ValueError("unterminated frontmatter")
        raise ValueError("missing frontmatter")

    block = match.group(1)
    fields: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def require_fields(path: Path, fields: tuple[str, ...], findings: list[Finding]) -> None:
    try:
        parsed = parse_frontmatter(path)
    except ValueError as error:
        findings.append(
            Finding(
                code="FRONTMATTER_MISSING",
                message=str(error),
                path=str(path.relative_to(ROOT)),
            )
        )
        return

    for field in fields:
        if not parsed.get(field):
            findings.append(
                Finding(
                    code="FRONTMATTER_FIELD_MISSING",
                    message=f"required field '{field}' is missing or empty",
                    path=str(path.relative_to(ROOT)),
                )
            )

    if path.name == "SKILL.md":
        expected_name = path.parent.name
        skill_name = parsed.get("name", "")
        if skill_name and skill_name != expected_name:
            findings.append(
                Finding(
                    code="SKILL_NAME_MISMATCH",
                    message=f"frontmatter name '{skill_name}' must match folder '{expected_name}'",
                    path=str(path.relative_to(ROOT)),
                )
            )


def list_files(pattern: str) -> list[Path]:
    return sorted(ROOT.glob(pattern))


def check_required_artifacts(findings: list[Finding]) -> None:
    for artifact in REQUIRED_ARTIFACTS:
        if not (ROOT / artifact).exists():
            findings.append(
                Finding(
                    code="REQUIRED_ARTIFACT_MISSING",
                    message="required orchestration artifact is missing",
                    path=str(artifact),
                )
            )


def check_frontmatter_contracts(findings: list[Finding]) -> None:
    for path in list_files(".github/agents/*.agent.md"):
        require_fields(path, ("name", "description"), findings)
    for path in list_files(".github/prompts/*.prompt.md"):
        require_fields(path, ("agent", "description"), findings)
    for path in list_files(".github/instructions/*.instructions.md"):
        require_fields(path, ("applyTo", "description"), findings)
    for path in list_files(".github/skills/*/SKILL.md"):
        require_fields(path, ("name", "description"), findings)


def check_inventory_docs(findings: list[Finding]) -> None:
    docs_content: dict[Path, str] = {}
    for doc in INVENTORY_DOCS:
        doc_path = ROOT / doc
        if not doc_path.exists():
            findings.append(
                Finding(
                    code="INVENTORY_DOC_MISSING",
                    message="inventory documentation file is missing",
                    path=str(doc),
                )
            )
            continue
        docs_content[doc] = doc_path.read_text(encoding="utf-8")

    if not docs_content:
        return

    for artifact in REQUIRED_ARTIFACTS:
        needle = str(artifact).replace("\\", "/")
        for doc, content in docs_content.items():
            if needle not in content:
                findings.append(
                    Finding(
                        code="INVENTORY_REFERENCE_MISSING",
                        message=f"missing reference to '{needle}'",
                        path=str(doc),
                    )
                )


def check_orchestrator_presence(findings: list[Finding]) -> None:
    agent_files = list_files(".github/agents/*.agent.md")
    has_orchestrator = any(re.search(r"(orchestrator|coordinator)", p.name) for p in agent_files)
    if not has_orchestrator:
        findings.append(
            Finding(
                code="ORCHESTRATOR_AGENT_MISSING",
                message="no orchestrator/coordinator agent file found in .github/agents",
                path=".github/agents",
            )
        )


def evaluate_workspace(strict: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    check_frontmatter_contracts(findings)
    check_orchestrator_presence(findings)
    check_required_artifacts(findings)
    check_inventory_docs(findings)
    if strict:
        duplicate_codes = {f.code for f in findings}
        if "FRONTMATTER_MISSING" in duplicate_codes:
            findings.append(
                Finding(
                    code="STRICT_FRONTMATTER_FAILURE",
                    message=(
                        "strict mode requires all customization artifacts to have valid frontmatter"
                    ),
                )
            )
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify customization harness integrity")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation mode")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = evaluate_workspace(strict=args.strict)
    if args.json:
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    elif findings:
        print("[verify-agent-harness] FAIL")
        for finding in findings:
            suffix = f" ({finding.path})" if finding.path else ""
            print(f"- {finding.code}: {finding.message}{suffix}")
    else:
        print("[verify-agent-harness] PASS")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
