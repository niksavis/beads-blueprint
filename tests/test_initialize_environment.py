"""Tests for scripts/initialize_environment.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace

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


def test_report_setup_artifact_changes_prints_commit_hint(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
            return SimpleNamespace(returncode=0, stdout="true\n", stderr="")
        if command[:3] == ["git", "status", "--short"]:
            return SimpleNamespace(
                returncode=0,
                stdout=" M .gitignore\n?? .beads/hooks/pre-push\n",
                stderr="",
            )

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.report_setup_artifact_changes(Path("."))

    output = capsys.readouterr().out
    assert "Bootstrap changed tracked setup artifacts:" in output
    assert "git add .gitignore .beads/hooks" in output
    assert "chore(setup): record beads bootstrap artifacts (bd-setup)" in output


def test_report_setup_artifact_changes_noop_when_clean(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
            return SimpleNamespace(returncode=0, stdout="true\n", stderr="")
        if command[:3] == ["git", "status", "--short"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.report_setup_artifact_changes(Path("."))

    output = capsys.readouterr().out
    assert output == ""


def test_report_setup_artifact_changes_handles_non_utf8_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
            return SimpleNamespace(returncode=0, stdout=b"true\n", stderr=b"")
        if command[:3] == ["git", "status", "--short"]:
            return SimpleNamespace(
                returncode=0,
                stdout=b" M .gitignore\n?? .beads/hooks/pre-push\x8f\n",
                stderr=b"",
            )

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.report_setup_artifact_changes(Path("."))

    output = capsys.readouterr().out
    assert "Bootstrap changed tracked setup artifacts:" in output


def test_print_post_init_workflow_hint_when_beads_exists(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()
    monkeypatch.setattr(module, "_is_beads_initialized", lambda _repo_root: True)

    module.print_post_init_workflow_hint(tmp_path)

    output = capsys.readouterr().out
    assert ".github/prompts/start-work-session.prompt.md" in output
    assert 'bd create "Describe task" --description' in output
    assert "bd update <id> --claim --json" in output
    assert "3-7 step implementation plan" in output


def test_print_post_init_workflow_hint_noop_without_beads(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()
    monkeypatch.setattr(module, "_is_beads_initialized", lambda _repo_root: False)

    module.print_post_init_workflow_hint(tmp_path)

    output = capsys.readouterr().out
    assert output == ""


def test_maybe_reload_vscode_window_skips_without_cli(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()
    monkeypatch.setattr(module, "locate_vscode_cli", lambda: None)

    module.maybe_reload_vscode_window(Path("/tmp/my-project"))

    output = capsys.readouterr().out
    assert "Skipping VS Code reload: VS Code CLI is not available in PATH." in output


def test_maybe_reload_vscode_window_skips_when_repo_window_not_open(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()
    monkeypatch.setattr(module, "locate_vscode_cli", lambda: "code")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command == ["code", "--status"]:
            return SimpleNamespace(
                returncode=0, stdout=b"window [1] (Welcome - Visual Studio Code)", stderr=b""
            )

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.maybe_reload_vscode_window(Path("/tmp/my-project"))

    output = capsys.readouterr().out
    assert "no open VS Code window found for this repository" in output


def test_maybe_reload_vscode_window_triggers_reload_for_repo_window(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()
    monkeypatch.setattr(module, "locate_vscode_cli", lambda: "code")

    calls: list[list[str]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        calls.append(command)
        if command == ["code", "--status"]:
            return SimpleNamespace(
                returncode=0,
                stdout=b"window [33] (my-project - Visual Studio Code)",
                stderr=b"",
            )
        if len(command) >= 6 and command[:2] == ["code", "--folder-uri"]:
            return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.maybe_reload_vscode_window(Path("/tmp/my-project"))

    assert calls[0] == ["code", "--status"]
    assert calls[1][0:2] == ["code", "--folder-uri"]
    assert "--command" in calls[1]
    assert "workbench.action.reloadWindow" in calls[1]
    output = capsys.readouterr().out
    assert "Triggered VS Code window reload for this repository." in output


def test_is_beads_initialized_uses_bd_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(module, "locate_bd", lambda _repo_root: "bd")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command == ["bd", "info", "--json"]:
            return SimpleNamespace(returncode=0, stdout="{}", stderr="")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module._is_beads_initialized(Path(".")) is True


def test_is_beads_initialized_returns_false_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(module, "locate_bd", lambda _repo_root: "bd")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, check
        if command == ["bd", "info", "--json"]:
            return SimpleNamespace(returncode=1, stdout="", stderr="no db")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module._is_beads_initialized(Path(".")) is False


def test_derive_issue_prefix_normalizes_repo_name() -> None:
    module = _load_initialize_environment_module()

    assert module.derive_issue_prefix(Path("My Project")) == "my-project"
    assert module.derive_issue_prefix(Path("___")) == "project"


def test_ensure_repo_issue_prefix_sets_missing_prefix(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()

    calls: list[list[str]] = []
    monkeypatch.setattr(module, "locate_bd", lambda _repo_root: "bd")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        encoding: str,
        errors: str,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, encoding, errors, check
        calls.append(command)
        if command in (
            ["bd", "config", "set", "issue_prefix", "my-project"],
            ["bd", "config", "set", "issue-prefix", "my-project"],
            ["bd", "config", "set", "id.prefix", "my-project"],
        ):
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.ensure_repo_issue_prefix(Path("/tmp/my-project"))

    assert calls == [
        ["bd", "config", "set", "issue_prefix", "my-project"],
        ["bd", "config", "set", "issue-prefix", "my-project"],
        ["bd", "config", "set", "id.prefix", "my-project"],
    ]
    output = capsys.readouterr().out
    assert "Configured Beads issue prefix: my-project" in output


def test_ensure_repo_issue_prefix_succeeds_when_any_key_is_supported(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(module, "locate_bd", lambda _repo_root: "bd")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        encoding: str,
        errors: str,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, encoding, errors, check
        if command == ["bd", "config", "set", "issue_prefix", "my-project"]:
            return SimpleNamespace(returncode=1, stdout="", stderr="unknown key")
        if command == ["bd", "config", "set", "issue-prefix", "my-project"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command == ["bd", "config", "set", "id.prefix", "my-project"]:
            return SimpleNamespace(returncode=1, stdout="", stderr="unknown key")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.ensure_repo_issue_prefix(Path("/tmp/my-project"))

    output = capsys.readouterr().out
    assert "Configured Beads issue prefix: my-project" in output


def test_ensure_repo_issue_prefix_raises_when_no_key_is_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_initialize_environment_module()

    monkeypatch.setattr(module, "locate_bd", lambda _repo_root: "bd")

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        encoding: str,
        errors: str,
        check: bool,
    ) -> SimpleNamespace:
        del cwd, capture_output, text, encoding, errors, check
        if command in (
            ["bd", "config", "set", "issue_prefix", "my-project"],
            ["bd", "config", "set", "issue-prefix", "my-project"],
            ["bd", "config", "set", "id.prefix", "my-project"],
        ):
            return SimpleNamespace(returncode=1, stdout="", stderr="unknown key")

        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="Failed to set Beads issue prefix"):
        module.ensure_repo_issue_prefix(Path("/tmp/my-project"))
