"""Tests for scripts/verify_agent_harness.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_verify_module() -> ModuleType:
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "verify_agent_harness.py"
    spec = importlib.util.spec_from_file_location("verify_agent_harness", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load verify_agent_harness.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_verify_agent_harness_passes_on_repository_state() -> None:
    module = _load_verify_module()
    findings = module.evaluate_workspace(strict=True)
    assert findings == []


def test_verify_agent_harness_reports_missing_required_artifact(
    monkeypatch,
) -> None:
    module = _load_verify_module()
    monkeypatch.setattr(module, "REQUIRED_ARTIFACTS", (Path(".github/agents/not-there.agent.md"),))
    findings = module.evaluate_workspace(strict=False)
    assert any(f.code == "REQUIRED_ARTIFACT_MISSING" for f in findings)


def test_parse_frontmatter_accepts_crlf_newlines(tmp_path) -> None:
    module = _load_verify_module()
    frontmatter_file = tmp_path / "frontmatter.md"
    frontmatter_file.write_text(
        '---\r\nname: "example"\r\ndescription: "desc"\r\n---\r\ncontent\r\n',
        encoding="utf-8",
    )

    parsed = module.parse_frontmatter(frontmatter_file)

    assert parsed["name"] == "example"
    assert parsed["description"] == "desc"


def test_verify_agent_harness_strict_flags_missing_frontmatter(
    monkeypatch,
    tmp_path,
) -> None:
    module = _load_verify_module()
    bad_agent = tmp_path / ".github" / "agents" / "bad.agent.md"
    bad_agent.parent.mkdir(parents=True, exist_ok=True)
    bad_agent.write_text("No frontmatter here\n", encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "REQUIRED_ARTIFACTS", ())
    monkeypatch.setattr(module, "INVENTORY_DOCS", ())

    findings = module.evaluate_workspace(strict=True)
    codes = {f.code for f in findings}

    assert "FRONTMATTER_MISSING" in codes
    assert "STRICT_FRONTMATTER_FAILURE" in codes


def test_verify_agent_harness_reports_missing_inventory_reference(
    monkeypatch,
    tmp_path,
) -> None:
    module = _load_verify_module()
    inventory_doc = tmp_path / ".github" / "copilot_customization.md"
    inventory_doc.parent.mkdir(parents=True, exist_ok=True)
    inventory_doc.write_text("# Inventory\n", encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "REQUIRED_ARTIFACTS",
        (Path(".github/agents/work-orchestrator.agent.md"),),
    )
    monkeypatch.setattr(module, "INVENTORY_DOCS", (Path(".github/copilot_customization.md"),))

    findings: list[Any] = []
    module.check_inventory_docs(findings)

    assert any(f.code == "INVENTORY_REFERENCE_MISSING" for f in findings)
