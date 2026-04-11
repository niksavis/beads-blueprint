"""Tests for install_hooks.py managed hook templates."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
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
    assert 'run_beads_core_hook pre-commit "$@"' in module.PRE_COMMIT
    assert '"$PYTHON" validate.py --commit' in module.PRE_COMMIT
    assert "beads_hook_has_validate" not in module.PRE_COMMIT


def test_pre_push_runs_local_validate_and_beads_core_hook() -> None:
    module = _load_install_hooks_module()
    assert 'run_beads_core_hook pre-push "$@"' in module.PRE_PUSH
    assert '"$PYTHON" validate.py' in module.PRE_PUSH
    assert "beads_hook_has_validate" not in module.PRE_PUSH


def test_file_delegated_templates_do_not_embed_bd_hooks_run_logic() -> None:
    module = _load_install_hooks_module()
    templates = (
        module.COMMIT_MSG,
        module.POST_MERGE,
        module.POST_REWRITE,
    )
    for template in templates:
        assert "bd hooks run" not in template


def test_commit_msg_hook_template_uses_native_bd_initialization_check() -> None:
    module = _load_install_hooks_module()

    assert "beads_initialized()" in module.COMMIT_MSG
    assert "bd info --json" in module.COMMIT_MSG
    assert "resolve_issue_prefix()" in module.COMMIT_MSG
    assert "bd config get --json issue_prefix" in module.COMMIT_MSG
    assert "bd config get --json issue-prefix" in module.COMMIT_MSG
    assert "ISSUE_PREFIX=$(resolve_issue_prefix || true)" in module.COMMIT_MSG
    assert 'bd show "$TRAILER" --json' in module.COMMIT_MSG


def _write_fake_bd(bin_dir: Path) -> None:
    fake_bd = bin_dir / "bd"
    fake_bd.write_text(
        """#!/usr/bin/env sh
set -eu

cmd="${1:-}"
if [ $# -gt 0 ]; then
    shift
fi

case "$cmd" in
    info)
        if [ "${FAKE_BD_INITIALIZED:-0}" = "1" ] && [ "${1:-}" = "--json" ]; then
            echo '{}'
            exit 0
        fi
        exit 1
        ;;
    config)
        sub="${1:-}"
        if [ $# -gt 0 ]; then
            shift
        fi

        case "$sub" in
            get)
                if [ "${1:-}" = "--json" ] && [ $# -gt 0 ]; then
                    shift
                fi

                key="${1:-}"
                case "$key" in
                    issue_prefix|issue-prefix|id.prefix)
                        if [ -n "${FAKE_BD_PREFIX:-}" ]; then
                            printf '{"key":"%s","value":"%s"}\n' "$key" "$FAKE_BD_PREFIX"
                            exit 0
                        fi
                        ;;
                esac
                exit 1
                ;;
            list)
                if [ -n "${FAKE_BD_PREFIX:-}" ]; then
                    printf 'issue_prefix = %s\n' "$FAKE_BD_PREFIX"
                    exit 0
                fi
                exit 1
                ;;
        esac
        exit 1
        ;;
    show)
        issue="${1:-}"
        case ",${FAKE_BD_VALID_IDS:-}," in
            *,"$issue",*)
                exit 0
                ;;
        esac
        exit 1
        ;;
esac

exit 1
""",
        encoding="utf-8",
    )
    fake_bd.chmod(0o755)


def _run_commit_msg_hook(
    tmp_path: Path,
    *,
    first_line: str,
    initialized: bool,
    prefix: str,
    valid_ids: str,
) -> subprocess.CompletedProcess[str]:
    sh_bin = shutil.which("sh")
    if sh_bin is None:
        pytest.skip("Shell interpreter is required to execute hook behavior tests")

    module = _load_install_hooks_module()

    hook_path = tmp_path / "commit-msg"
    hook_path.write_text(module.COMMIT_MSG, encoding="utf-8")
    hook_path.chmod(0o755)

    commit_msg_file = tmp_path / "COMMIT_EDITMSG"
    commit_msg_file.write_text(f"{first_line}\n", encoding="utf-8")

    (tmp_path / ".beads" / "hooks").mkdir(parents=True, exist_ok=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    _write_fake_bd(bin_dir)

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["FAKE_BD_INITIALIZED"] = "1" if initialized else "0"
    env["FAKE_BD_PREFIX"] = prefix
    env["FAKE_BD_VALID_IDS"] = valid_ids

    return subprocess.run(
        [sh_bin, str(hook_path), str(commit_msg_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_commit_msg_hook_accepts_existing_issue_with_exact_prefix(tmp_path: Path) -> None:
    result = _run_commit_msg_hook(
        tmp_path,
        first_line="feat(core): add flow (my-project-123)",
        initialized=True,
        prefix="my-project",
        valid_ids="my-project-123",
    )

    assert result.returncode == 0


def test_commit_msg_hook_rejects_bd_prefix_when_repo_prefix_differs(tmp_path: Path) -> None:
    result = _run_commit_msg_hook(
        tmp_path,
        first_line="feat(core): add flow (bd-123)",
        initialized=True,
        prefix="my-project",
        valid_ids="my-project-123,bd-123",
    )

    assert result.returncode != 0
    assert "expected exact Beads trailer" in result.stderr


def test_commit_msg_hook_rejects_unknown_issue_id(tmp_path: Path) -> None:
    result = _run_commit_msg_hook(
        tmp_path,
        first_line="feat(core): add flow (my-project-999)",
        initialized=True,
        prefix="my-project",
        valid_ids="",
    )

    assert result.returncode != 0
    assert "does not resolve" in result.stderr
    assert "existing Beads issue" in result.stderr


def test_commit_msg_hook_requires_trailer_when_initialized(tmp_path: Path) -> None:
    result = _run_commit_msg_hook(
        tmp_path,
        first_line="feat(core): add flow",
        initialized=True,
        prefix="my-project",
        valid_ids="my-project-123",
    )

    assert result.returncode != 0
    assert "Missing Beads trailer" in result.stderr


def test_commit_msg_hook_skips_enforcement_when_beads_not_initialized(tmp_path: Path) -> None:
    result = _run_commit_msg_hook(
        tmp_path,
        first_line="feat(core): add flow",
        initialized=False,
        prefix="my-project",
        valid_ids="",
    )

    assert result.returncode == 0


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
    tmp_path: Path,
) -> None:
    module = _load_install_hooks_module()

    call_order: list[str] = []

    monkeypatch.setattr(module, "_refresh_beads_hooks", lambda: call_order.append("refresh"))

    def fake_ensure_managed_hooks_path(*, check_only: bool) -> bool:
        assert check_only is False
        call_order.append("ensure")
        return True

    monkeypatch.setattr(module, "_ensure_managed_hooks_path", fake_ensure_managed_hooks_path)
    monkeypatch.setattr(module, "HOOKS_DIR", tmp_path / ".git" / "hooks")
    monkeypatch.setattr(module, "HOOKS", {})

    assert module.install(check_only=False, force=True) == 0
    assert call_order == ["refresh", "ensure"]
