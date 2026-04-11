"""Tests for release metadata bootstrap behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_module(module_name: str, file_name: str) -> ModuleType:
    module_path = Path(__file__).resolve().parents[1] / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {file_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_read_version_bootstraps_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module("release_bootstrap_release", "release.py")
    version_file = tmp_path / "version.py"
    monkeypatch.setattr(module, "VERSION_FILE", version_file)

    assert module.read_version() == (0, 1, 0)
    assert version_file.exists()
    assert '__version__ = "0.1.0"' in version_file.read_text(encoding="utf-8")


def test_regenerate_read_version_bootstraps_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module("release_bootstrap_regen", "regenerate_changelog.py")
    version_file = tmp_path / "version.py"
    monkeypatch.setattr(module, "VERSION_FILE", version_file)

    assert module.read_version() == "0.1.0"
    assert version_file.exists()


def test_regenerate_ensure_version_section_creates_missing_changelog(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module("release_bootstrap_regen_changelog", "regenerate_changelog.py")
    changelog_file = tmp_path / "changelog.md"
    monkeypatch.setattr(module, "CHANGELOG_FILE", changelog_file)

    module.ensure_version_section("0.1.1", "2026-01-01")

    content = changelog_file.read_text(encoding="utf-8")
    assert "# Changelog" in content
    assert "## v0.1.1" in content


def test_generate_version_info_uses_default_when_missing_version_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module("release_bootstrap_version_info", "generate_version_info.py")
    monkeypatch.setattr(module, "VERSION_FILE", tmp_path / "version.py")

    assert module.read_version() == "0.1.0"
