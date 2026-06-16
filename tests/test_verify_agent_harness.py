"""Tests for scripts/verify_agent_harness.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


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
