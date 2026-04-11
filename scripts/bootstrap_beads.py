#!/usr/bin/env python3
"""Bootstrap Beads tooling for this repository.

Steps:
1. Install or verify Beads + Dolt (optional).
2. Install beads-mcp for GitHub Copilot MCP usage.
3. Configure user-level VS Code MCP entries for Beads.
4. Configure VS Code defaults for bash-first terminal usage.
5. Configure git merge driver for Beads JSONL merges.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

from configure_beads import configure_merge_driver
from install_beads import DEFAULT_BEADS_VERSION, ensure_beads_and_dolt


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_json_object(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Unable to update MCP config at {path}: file contains invalid JSON."
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            f"Unable to update MCP config at {path}: top-level value must be a JSON object."
        )

    return payload


def ensure_beads_mcp_installed() -> None:
    if shutil.which("beads-mcp"):
        print("beads-mcp MCP server is already available.")
        return

    uv_bin = shutil.which("uv")
    if not uv_bin:
        raise RuntimeError(
            "uv is required to install beads-mcp. Install uv, then run: uv tool install beads-mcp"
        )

    result = subprocess.run(
        [uv_bin, "tool", "install", "beads-mcp"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(
        part.strip() for part in (result.stdout or "", result.stderr or "") if part.strip()
    )
    output_lower = output.lower()

    if result.returncode == 0 or "already installed" in output_lower:
        print("Ensured beads-mcp MCP server is installed.")
        return

    raise RuntimeError(
        "Failed to install beads-mcp using uv. "
        "Run 'uv tool install beads-mcp' and retry bootstrap.\n"
        f"Details:\n{output or '(no output)'}"
    )


def _vscode_user_mcp_path() -> Path | None:
    system = platform.system()
    if system == "Windows":
        app_data = os.environ.get("APPDATA")
        if not app_data:
            return None
        return Path(app_data) / "Code" / "User" / "mcp.json"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
    return Path.home() / ".config" / "Code" / "User" / "mcp.json"


def _merge_beads_mcp_server(config: dict) -> bool:
    servers = config.get("servers")
    if servers is None:
        servers = {}
        config["servers"] = servers

    if not isinstance(servers, dict):
        raise RuntimeError("Unable to update MCP config: 'servers' must be a JSON object.")

    existing = servers.get("beads")
    desired_command = "beads-mcp"

    if isinstance(existing, dict):
        updated = dict(existing)
        updated["command"] = desired_command
        if updated == existing:
            return False
        servers["beads"] = updated
        return True

    if existing == {"command": desired_command}:
        return False

    servers["beads"] = {"command": desired_command}
    return True


def _ensure_mcp_config(path: Path) -> None:
    config = load_json_object(path)
    changed = _merge_beads_mcp_server(config)
    if path.exists() and not changed:
        print(f"MCP config already contains beads server: {path}")
        return

    write_json(path, config)
    print(f"Updated MCP config: {path}")


def update_user_vscode_mcp_config() -> None:
    user_mcp_path = _vscode_user_mcp_path()
    if user_mcp_path is None:
        raise RuntimeError("Unable to resolve VS Code user mcp.json path.")

    _ensure_mcp_config(user_mcp_path)


def ensure_git_bash_init_file(repo_root: Path) -> None:
    init_file = repo_root / ".vscode" / "git-bash-init.sh"
    content = (
        "# VS Code Git Bash init file.\n"
        "# Activate the local Windows virtual environment when present.\n"
        "# Do not fail if the virtual environment has not been created yet.\n"
        'if [ -f ".venv/Scripts/activate" ]; then\n'
        '  . ".venv/Scripts/activate"\n'
        "fi\n"
    )
    init_file.parent.mkdir(parents=True, exist_ok=True)
    init_file.write_text(content, encoding="utf-8", newline="\n")


def update_vscode_settings(repo_root: Path) -> None:
    ensure_git_bash_init_file(repo_root)
    settings_path = repo_root / ".vscode" / "settings.json"
    settings = load_json(settings_path)

    settings["python.terminal.activateEnvironment"] = False
    settings["terminal.integrated.defaultProfile.windows"] = "Git Bash (.venv)"
    settings["terminal.integrated.defaultProfile.linux"] = "bash"
    settings["terminal.integrated.defaultProfile.osx"] = "bash"

    profiles_windows = settings.get("terminal.integrated.profiles.windows", {})
    profiles_windows["Git Bash (.venv)"] = {
        "source": "Git Bash",
        "args": ["--init-file", ".vscode/git-bash-init.sh"],
        "icon": "terminal-bash",
    }
    profiles_windows["Git Bash"] = {
        "source": "Git Bash",
        "icon": "terminal-bash",
    }
    profiles_windows["PowerShell (.venv)"] = {
        "source": "PowerShell",
        "args": ["-NoExit", "-Command", "& '.venv\\Scripts\\Activate.ps1'"],
    }
    profiles_windows["PowerShell"] = {"source": "PowerShell"}
    settings["terminal.integrated.profiles.windows"] = profiles_windows

    settings.pop("terminal.integrated.env.windows", None)
    settings.pop("terminal.integrated.env.linux", None)
    settings.pop("terminal.integrated.env.osx", None)

    write_json(settings_path, settings)
    print(f"Updated VS Code settings: {settings_path}")


def update_vscode_tasks(repo_root: Path) -> None:
    tasks_path = repo_root / ".vscode" / "tasks.json"
    tasks_json = load_json(tasks_path)
    existing_tasks = tasks_json.get("tasks", [])

    required = {
        "Beads Fetch Issues": {
            "label": "Beads Fetch Issues",
            "type": "shell",
            "command": "bd backup fetch-git",
            "problemMatcher": [],
        },
        "Beads Export Issues": {
            "label": "Beads Export Issues",
            "type": "shell",
            "command": "bd backup export-git",
            "problemMatcher": [],
        },
    }

    by_label = {task.get("label", ""): task for task in existing_tasks if isinstance(task, dict)}
    for label in ("Start Beads Daemon", "Beads Import", "Quality Gate (fast)"):
        by_label.pop(label, None)
    for label, task in required.items():
        task["isBackground"] = False
        by_label[label] = task

    tasks_json["version"] = "2.0.0"
    tasks_json["tasks"] = list(by_label.values())
    write_json(tasks_path, tasks_json)
    print(f"Updated VS Code tasks: {tasks_path}")


def verify_tool(name: str, version_args: list[str]) -> bool:
    binary = shutil.which(name) or ""
    if not binary:
        print(f"Warning: could not locate {name} after bootstrap.")
        return False

    result = subprocess.run([binary, *version_args], capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout.strip() or result.stderr.strip()
        print(output)
        return True
    else:
        print(f"Warning: {name} version check failed")
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install and configure Beads for this repo")
    parser.add_argument("--skip-install", action="store_true", help="Skip tool installation")
    parser.add_argument("--force", action="store_true", help="Force reinstall of Beads and Dolt")
    parser.add_argument(
        "--beads-version",
        default=DEFAULT_BEADS_VERSION,
        help="Beads version tag (default: v0.63.3)",
    )
    parser.add_argument("--dolt-version", help="Optional Dolt version tag")
    parser.add_argument(
        "--update-tools",
        action="store_true",
        help="Update Beads and Dolt even if both are already available",
    )
    parser.add_argument("--yes-to-all", action="store_true", help="Auto-answer prompts")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    install_result: dict[str, str | bool] | None = None

    if not args.skip_install:
        install_result = ensure_beads_and_dolt(
            force=args.force,
            beads_version=args.beads_version,
            dolt_version=args.dolt_version,
            assume_yes=args.yes_to_all,
            update_existing=args.update_tools,
        )

    bd_binary = ""
    if install_result is not None:
        bd_binary = str(install_result.get("bd_binary", "") or "")
    if not bd_binary:
        bd_binary = shutil.which("bd") or ""

    if not bd_binary:
        raise RuntimeError(
            "Beads CLI (bd) is required before MCP setup. Install or expose bd in PATH, then retry."
        )

    ensure_beads_mcp_installed()
    update_user_vscode_mcp_config()

    update_vscode_settings(repo_root)
    update_vscode_tasks(repo_root)
    configure_merge_driver(repo_root)

    bd_ok = verify_tool("bd", ["--version"])
    dolt_ok = verify_tool("dolt", ["version"])
    if install_result is not None and not (bd_ok and dolt_ok):
        raise RuntimeError(
            "Tool bootstrap verification failed: expected bd and dolt to be available."
        )

    print("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
