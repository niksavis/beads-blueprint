"""Tests for scripts/bootstrap_beads.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_bootstrap_beads_module() -> ModuleType:
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    module_path = scripts_dir / "bootstrap_beads.py"
    spec = importlib.util.spec_from_file_location("bootstrap_beads", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load bootstrap_beads.py")

    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(scripts_dir))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def test_write_json_uses_explicit_lf_newline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_bootstrap_beads_module()
    captured: dict[str, object] = {}

    def fake_write_text(
        self: Path,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        del errors
        captured["path"] = self
        captured["data"] = data
        captured["encoding"] = encoding
        captured["newline"] = newline
        return len(data)

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    target = tmp_path / ".vscode" / "settings.json"
    module.write_json(target, {"alpha": 1})

    assert captured["path"] == target
    assert captured["encoding"] == "utf-8"
    assert captured["newline"] == "\n"
    assert str(captured["data"]).endswith("\n")


def test_vscode_json_files_written_with_lf_line_endings(tmp_path: Path) -> None:
    module = _load_bootstrap_beads_module()
    module.update_vscode_settings(tmp_path)
    module.update_vscode_tasks(tmp_path)

    settings_path = tmp_path / ".vscode" / "settings.json"
    tasks_path = tmp_path / ".vscode" / "tasks.json"

    settings_bytes = settings_path.read_bytes()
    tasks_bytes = tasks_path.read_bytes()

    assert b"\r\n" not in settings_bytes
    assert b"\r\n" not in tasks_bytes

    assert isinstance(json.loads(settings_bytes.decode("utf-8")), dict)
    assert isinstance(json.loads(tasks_bytes.decode("utf-8")), dict)


def test_ensure_mcp_config_preserves_existing_servers(tmp_path: Path) -> None:
    module = _load_bootstrap_beads_module()
    mcp_path = tmp_path / "mcp.json"
    mcp_path.write_text(
        json.dumps(
            {
                "servers": {
                    "other": {"command": "other-mcp", "args": ["--flag"]},
                    "beads": {"args": ["--debug"]},
                }
            }
        ),
        encoding="utf-8",
    )

    module._ensure_mcp_config(mcp_path)

    payload = json.loads(mcp_path.read_text(encoding="utf-8"))
    assert payload["servers"]["other"] == {"command": "other-mcp", "args": ["--flag"]}
    assert payload["servers"]["beads"]["command"] == "beads-mcp"
    assert payload["servers"]["beads"]["args"] == ["--debug"]


def test_ensure_mcp_config_fails_on_invalid_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_bootstrap_beads_module()
    mcp_path = tmp_path / "mcp.json"
    original = "{not-valid-json"
    mcp_path.write_text(original, encoding="utf-8")

    with pytest.raises(RuntimeError, match="invalid JSON"):
        module._ensure_mcp_config(mcp_path)

    assert mcp_path.read_text(encoding="utf-8") == original
    output = capsys.readouterr().out
    assert output == ""


def test_update_user_vscode_mcp_config_writes_user_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_bootstrap_beads_module()

    appdata_root = tmp_path / "AppData" / "Roaming"
    monkeypatch.setenv("APPDATA", str(appdata_root))
    monkeypatch.setattr(module.platform, "system", lambda: "Windows")

    module.update_user_vscode_mcp_config()

    user_mcp = appdata_root / "Code" / "User" / "mcp.json"

    user_payload = json.loads(user_mcp.read_text(encoding="utf-8"))

    assert user_payload["servers"]["beads"]["command"] == "beads-mcp"
