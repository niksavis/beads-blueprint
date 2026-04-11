"""Tests for scripts/initialize_environment.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_initialize_environment_module() -> ModuleType:
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "initialize_environment.py"
    spec = importlib.util.spec_from_file_location("initialize_environment", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load initialize_environment.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_version_triplet_accepts_node_style_prefix() -> None:
    module = _load_initialize_environment_module()
    assert module._parse_version_triplet("v20.11.1", label="Node") == (20, 11, 1)


def test_build_bd_init_commands_prefers_server_mode() -> None:
    module = _load_initialize_environment_module()
    commands = module._build_bd_init_commands(
        "bd",
        "--help --skip-agents --non-interactive --server",
    )
    assert commands[0] == ["bd", "init", "--skip-agents", "--non-interactive", "--server"]


def test_resolve_python_interpreter_uses_supported_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(
        module,
        "discover_python_interpreters",
        lambda _repo_root: [
            ("python312", (3, 12, 7)),
            ("python314", (3, 14, 2)),
        ],
    )

    resolved = module.resolve_python_interpreter(
        requested_python=None,
        repo_root=Path("."),
        auto_install_missing=False,
    )
    assert resolved == "python314"


def test_resolve_python_interpreter_retries_after_auto_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    state = {"calls": 0}

    def fake_discover(_repo_root: Path) -> list[tuple[str, tuple[int, int, int]]]:
        state["calls"] += 1
        if state["calls"] == 1:
            return []
        return [("python314", (3, 14, 0))]

    monkeypatch.setattr(module, "discover_python_interpreters", fake_discover)
    monkeypatch.setattr(module, "auto_install_python", lambda _repo_root: True)

    resolved = module.resolve_python_interpreter(
        requested_python=None,
        repo_root=Path("."),
        auto_install_missing=True,
    )
    assert resolved == "python314"


def test_ensure_node_toolchain_attempts_auto_install(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_initialize_environment_module()

    state = {"calls": 0}

    def fake_detect() -> tuple[str | None, str | None]:
        state["calls"] += 1
        if state["calls"] == 1:
            return None, None
        return "node", "npm"

    monkeypatch.setattr(module, "_detect_node_binaries", fake_detect)
    monkeypatch.setattr(module, "auto_install_node", lambda _repo_root: True)
    monkeypatch.setattr(module, "node_version", lambda _node_bin, _repo_root: (20, 10, 1))

    node_bin, npm_bin = module.ensure_node_toolchain(Path("."), auto_install_missing=True)
    assert (node_bin, npm_bin) == ("node", "npm")


def test_ensure_node_toolchain_fails_when_node_is_too_old(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(module, "_detect_node_binaries", lambda: ("node", "npm"))
    monkeypatch.setattr(module, "node_version", lambda _node_bin, _repo_root: (18, 19, 0))
    monkeypatch.setattr(module, "auto_install_node", lambda _repo_root: False)

    with pytest.raises(RuntimeError, match="Node.js 20\\+"):
        module.ensure_node_toolchain(Path("."), auto_install_missing=True)
