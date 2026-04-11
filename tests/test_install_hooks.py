"""Tests for install_hooks.py managed hook templates."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_install_hooks_module() -> ModuleType:
    module_path = Path(__file__).resolve().parents[1] / "install_hooks.py"
    spec = importlib.util.spec_from_file_location("install_hooks", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load install_hooks.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pre_commit_delegates_to_beads_hook_file() -> None:
    module = _load_install_hooks_module()
    assert 'run_beads_hook_file pre-commit "$@"' in module.PRE_COMMIT


def test_hook_templates_do_not_embed_bd_hooks_run_logic() -> None:
    module = _load_install_hooks_module()
    templates = (
        module.PRE_COMMIT,
        module.PRE_PUSH,
        module.COMMIT_MSG,
        module.POST_MERGE,
        module.POST_REWRITE,
    )
    for template in templates:
        assert "bd hooks run" not in template


def test_check_mode_detects_non_managed_hooks_path(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_install_hooks_module()
    monkeypatch.setattr(module, "HOOKS_DIR", Path("/repo/.git/hooks"))
    monkeypatch.setattr(module, "_effective_hooks_dir", lambda: Path("/repo/.beads/hooks"))

    assert module._ensure_managed_hooks_path(check_only=True) is False


def test_check_mode_passes_for_managed_hooks_path(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_install_hooks_module()
    monkeypatch.setattr(module, "HOOKS_DIR", Path("/repo/.git/hooks"))
    monkeypatch.setattr(module, "_effective_hooks_dir", lambda: Path("/repo/.git/hooks").resolve())

    assert module._ensure_managed_hooks_path(check_only=True) is True


def test_install_refreshes_beads_hooks_before_setting_managed_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_install_hooks_module()

    call_order: list[str] = []

    monkeypatch.setattr(module, "_refresh_beads_hooks", lambda: call_order.append("refresh"))

    def fake_ensure_managed_hooks_path(*, check_only: bool) -> bool:
        assert check_only is False
        call_order.append("ensure")
        return True

    monkeypatch.setattr(module, "_ensure_managed_hooks_path", fake_ensure_managed_hooks_path)
    monkeypatch.setattr(module, "HOOKS_DIR", Path("/repo/.git/hooks"))
    monkeypatch.setattr(module, "HOOKS", {})

    assert module.install(check_only=False, force=True) == 0
    assert call_order == ["refresh", "ensure"]
