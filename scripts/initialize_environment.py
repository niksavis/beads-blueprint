#!/usr/bin/env python3
"""Initialize local development environment for this template.

This script is intentionally Python-first so the same command works on
Windows, macOS, and Linux. Repository markdown quality tooling relies
on Node via npm.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON_VERSION = (3, 14)
MIN_NODE_VERSION = (20, 0, 0)
PINNED_REQUIREMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[^\s]+(?:\s*;.+)?$"
)
ISSUE_PREFIX_SANITIZE_PATTERN = re.compile(r"[^a-z0-9._-]+")


def run(command: list[str], cwd: Path, check: bool = True) -> int:
    result = subprocess.run(command, cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    return result.returncode


def _as_text(output: bytes | str | None) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def _format_version(version: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in version)


def _version_at_least(version: tuple[int, ...], minimum: tuple[int, ...]) -> bool:
    return version[: len(minimum)] >= minimum


def _parse_version_triplet(raw: str, *, label: str) -> tuple[int, int, int]:
    value = raw.strip().lstrip("v")
    parts = value.split(".")
    if len(parts) < 2:
        raise RuntimeError(f"Unexpected {label} version output: {raw}")

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) >= 3 else 0
    except ValueError as exc:
        raise RuntimeError(f"Unexpected {label} version output: {raw}") from exc

    return major, minor, patch


def venv_python_path(repo_root: Path) -> Path:
    if sys.platform.startswith("win"):
        return repo_root / ".venv" / "Scripts" / "python.exe"
    return repo_root / ".venv" / "bin" / "python"


def python_version(python_bin: str | Path, cwd: Path) -> tuple[int, int, int]:
    code = "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"
    try:
        result = subprocess.run(
            [str(python_bin), "-c", code],
            cwd=cwd,
            capture_output=True,
            text=False,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Python interpreter not found: {python_bin}") from exc

    if result.returncode != 0:
        raise RuntimeError(f"Unable to determine Python version for interpreter: {python_bin}")

    output = _as_text(result.stdout).strip()
    return _parse_version_triplet(output, label="Python")


def ensure_min_python_version(python_bin: str | Path, repo_root: Path) -> None:
    version = python_version(python_bin, repo_root)
    if not _version_at_least(version, MIN_PYTHON_VERSION):
        required = _format_version(MIN_PYTHON_VERSION)
        actual = _format_version(version)
        raise RuntimeError(f"Python {required}+ is required, but found {actual} at: {python_bin}")


def _probe_python_command(
    command: list[str],
    repo_root: Path,
) -> tuple[str, tuple[int, int, int]] | None:
    probe_code = (
        "import sys; "
        "print(sys.executable); "
        "print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"
    )
    try:
        result = subprocess.run(
            [*command, "-c", probe_code],
            cwd=repo_root,
            capture_output=True,
            text=False,
            check=False,
        )
    except FileNotFoundError:
        return None

    if result.returncode != 0:
        return None

    output = _as_text(result.stdout)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    try:
        version = _parse_version_triplet(lines[1], label="Python")
    except RuntimeError:
        return None

    return lines[0], version


def _python_probe_commands() -> list[list[str]]:
    commands: list[list[str]] = []
    if sys.platform.startswith("win"):
        commands.extend(
            [
                ["py", "-3.14"],
                ["py", "-3"],
                ["python3.14"],
                ["python3"],
                ["python"],
            ]
        )
    else:
        commands.extend([["python3.14"], ["python3"], ["python"]])

    if sys.executable:
        commands.append([sys.executable])

    unique: list[list[str]] = []
    for command in commands:
        if command not in unique:
            unique.append(command)
    return unique


def discover_python_interpreters(repo_root: Path) -> list[tuple[str, tuple[int, int, int]]]:
    discovered: list[tuple[str, tuple[int, int, int]]] = []
    seen: set[str] = set()

    for command in _python_probe_commands():
        candidate = _probe_python_command(command, repo_root)
        if candidate is None:
            continue

        executable, version = candidate
        key = executable.lower() if sys.platform.startswith("win") else executable
        if key in seen:
            continue
        seen.add(key)
        discovered.append((executable, version))

    discovered.sort(key=lambda item: item[1], reverse=True)
    return discovered


def _run_install_steps(steps: list[list[str]], repo_root: Path) -> bool:
    for command in steps:
        print(f"Attempting tool install step: {' '.join(command)}")
        try:
            result = subprocess.run(command, cwd=repo_root, check=False)
        except FileNotFoundError:
            return False
        if result.returncode != 0:
            return False
    return True


def auto_install_python(repo_root: Path) -> bool:
    if sys.platform.startswith("win"):
        winget = shutil.which("winget")
        if not winget:
            return False

        commands = [
            [
                winget,
                "install",
                "--exact",
                "--id",
                "Python.Python.3.14",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            [
                winget,
                "install",
                "--exact",
                "--id",
                "Python.Python.3.14",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
        ]

        for command in commands:
            if _run_install_steps([command], repo_root):
                return True
        return False

    if sys.platform == "darwin":
        brew = shutil.which("brew")
        if not brew:
            return False
        return _run_install_steps([[brew, "install", "python@3.14"]], repo_root)

    if shutil.which("apt-get"):
        return _run_install_steps(
            [
                ["sudo", "-n", "apt-get", "update"],
                ["sudo", "-n", "apt-get", "install", "-y", "python3.14", "python3.14-venv"],
            ],
            repo_root,
        )
    if shutil.which("dnf"):
        return _run_install_steps(
            [["sudo", "-n", "dnf", "install", "-y", "python3.14"]],
            repo_root,
        )
    if shutil.which("pacman"):
        return _run_install_steps(
            [["sudo", "-n", "pacman", "-S", "--noconfirm", "python"]],
            repo_root,
        )
    return False


def resolve_python_interpreter(
    requested_python: str | None,
    repo_root: Path,
    auto_install_missing: bool,
) -> str:
    if requested_python:
        ensure_min_python_version(requested_python, repo_root)
        return requested_python

    candidates = discover_python_interpreters(repo_root)
    for executable, version in candidates:
        if _version_at_least(version, MIN_PYTHON_VERSION):
            return executable

    if auto_install_missing:
        print("No compatible Python found; trying automatic install of Python 3.14+...")
        if auto_install_python(repo_root):
            candidates = discover_python_interpreters(repo_root)
            for executable, version in candidates:
                if _version_at_least(version, MIN_PYTHON_VERSION):
                    return executable

    discovered_text = ", ".join(
        f"{path} ({_format_version(version)})" for path, version in candidates
    )
    if not discovered_text:
        discovered_text = "none"
    raise RuntimeError(
        "Unable to locate Python 3.14+ automatically. "
        f"Detected interpreters: {discovered_text}. "
        "Install Python 3.14+ and rerun initialization, or pass --python <path>."
    )


def _iter_lock_requirements(file_path: Path) -> list[str]:
    requirements: list[str] = []
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith((" ", "\t")):
            continue

        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-", "--")):
            continue

        requirements.append(line)
    return requirements


def ensure_pinned_lockfile(file_path: Path) -> None:
    for requirement in _iter_lock_requirements(file_path):
        if not PINNED_REQUIREMENT_PATTERN.match(requirement):
            raise RuntimeError(
                f"Unpinned or unsupported requirement in {file_path.name}: {requirement}"
            )


def ensure_venv(repo_root: Path, python_bin: str, recreate: bool) -> Path:
    venv_dir = repo_root / ".venv"
    if recreate and venv_dir.exists():
        shutil.rmtree(venv_dir)

    if not venv_dir.exists():
        print("Creating virtual environment...")
        run([python_bin, "-m", "venv", str(venv_dir)], cwd=repo_root)

    interpreter = venv_python_path(repo_root)
    if not interpreter.exists():
        raise RuntimeError(f"Virtual environment Python not found: {interpreter}")

    return interpreter


def node_version(node_bin: str | Path, cwd: Path) -> tuple[int, int, int]:
    try:
        result = subprocess.run(
            [str(node_bin), "--version"],
            cwd=cwd,
            capture_output=True,
            text=False,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Node executable not found: {node_bin}") from exc

    if result.returncode != 0:
        raise RuntimeError(f"Unable to determine Node version for executable: {node_bin}")

    output = _as_text(result.stdout).strip() or _as_text(result.stderr).strip()
    return _parse_version_triplet(output, label="Node")


def _detect_node_binaries() -> tuple[str | None, str | None]:
    node_bin = shutil.which("node")
    npm_bin = shutil.which("npm")

    if sys.platform.startswith("win"):
        program_files = os.environ.get("ProgramFiles")
        if program_files:
            node_candidate = Path(program_files) / "nodejs" / "node.exe"
            npm_candidate = Path(program_files) / "nodejs" / "npm.cmd"
            if node_bin is None and node_candidate.exists():
                node_bin = str(node_candidate)
            if npm_bin is None and npm_candidate.exists():
                npm_bin = str(npm_candidate)

    return node_bin, npm_bin


def auto_install_node(repo_root: Path) -> bool:
    if sys.platform.startswith("win"):
        winget = shutil.which("winget")
        if not winget:
            return False

        commands = [
            [
                winget,
                "install",
                "--exact",
                "--id",
                "OpenJS.NodeJS.LTS",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            [
                winget,
                "install",
                "--exact",
                "--id",
                "OpenJS.NodeJS.LTS",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
        ]

        for command in commands:
            if _run_install_steps([command], repo_root):
                return True
        return False

    if sys.platform == "darwin":
        brew = shutil.which("brew")
        if not brew:
            return False
        return _run_install_steps([[brew, "install", "node@20"]], repo_root)

    if shutil.which("apt-get"):
        return _run_install_steps(
            [
                ["sudo", "-n", "apt-get", "update"],
                ["sudo", "-n", "apt-get", "install", "-y", "nodejs", "npm"],
            ],
            repo_root,
        )
    if shutil.which("dnf"):
        return _run_install_steps(
            [["sudo", "-n", "dnf", "install", "-y", "nodejs", "npm"]],
            repo_root,
        )
    if shutil.which("pacman"):
        return _run_install_steps(
            [["sudo", "-n", "pacman", "-S", "--noconfirm", "nodejs", "npm"]],
            repo_root,
        )
    return False


def ensure_node_toolchain(repo_root: Path, auto_install_missing: bool) -> tuple[str, str]:
    node_bin, npm_bin = _detect_node_binaries()

    if auto_install_missing and (node_bin is None or npm_bin is None):
        print("Node.js/npm not found; trying automatic install of Node.js LTS...")
        if auto_install_node(repo_root):
            node_bin, npm_bin = _detect_node_binaries()

    if node_bin is None or npm_bin is None:
        raise RuntimeError(
            "Node.js 20+ and npm are required for markdown tooling. "
            "Install Node.js LTS and rerun, or pass --skip-node-tools."
        )

    version = node_version(node_bin, repo_root)
    if not _version_at_least(version, MIN_NODE_VERSION):
        if auto_install_missing:
            print("Node.js version is below 20; trying automatic upgrade...")
            if auto_install_node(repo_root):
                node_bin, npm_bin = _detect_node_binaries()
                if node_bin is None or npm_bin is None:
                    raise RuntimeError(
                        "Automatic Node.js installation completed but binaries were "
                        "not found in PATH. Restart terminal and rerun initialization."
                    )
                version = node_version(node_bin, repo_root)

        if not _version_at_least(version, MIN_NODE_VERSION):
            required = _format_version(MIN_NODE_VERSION[:1])
            actual = _format_version(version)
            raise RuntimeError(
                f"Node.js {required}+ is required, but found {actual} at: {node_bin}."
            )

    return node_bin, npm_bin


def install_requirements(repo_root: Path, interpreter: Path, upgrade_pip: bool) -> None:
    print("Installing Python dependencies...")
    lockfiles = ("requirements.txt", "requirements-dev.txt")
    missing = [name for name in lockfiles if not (repo_root / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing lockfile(s): {joined}")

    if upgrade_pip:
        run(
            [str(interpreter), "-m", "pip", "install", "--upgrade", "pip"],
            cwd=repo_root,
        )

    for filename in lockfiles:
        ensure_pinned_lockfile(repo_root / filename)
        run(
            [
                str(interpreter),
                "-m",
                "pip",
                "install",
                "--require-virtualenv",
                "-r",
                filename,
            ],
            cwd=repo_root,
        )


def install_node_dependencies(
    repo_root: Path,
    skip_node_tools: bool,
    auto_install_missing: bool,
) -> None:
    package_json = repo_root / "package.json"
    if skip_node_tools or not package_json.exists():
        return

    _, npm_bin = ensure_node_toolchain(repo_root, auto_install_missing)

    package_lock = repo_root / "package-lock.json"
    if not package_lock.exists():
        raise RuntimeError(
            "package-lock.json is required for reproducible Node installs. "
            "Generate and commit it, then rerun initialization."
        )

    npm_command = [npm_bin, "ci"]
    print("Installing Node tooling...")
    run(npm_command, cwd=repo_root)


def locate_bd(repo_root: Path) -> str | None:
    in_path = shutil.which("bd")
    return in_path


def locate_vscode_cli() -> str | None:
    for candidate in ("code", "code-insiders"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _normalize_for_match(value: str) -> str:
    return value.replace("\\", "/").casefold()


def _is_repo_window_open_in_vscode(code_bin: str, repo_root: Path) -> bool:
    result = subprocess.run(
        [code_bin, "--status"],
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    if result.returncode != 0:
        return False

    stdout = _as_text(result.stdout)
    stderr = _as_text(result.stderr)
    status_text = "\n".join(part for part in (stdout, stderr) if part)

    normalized_status = _normalize_for_match(status_text)
    repo_path = _normalize_for_match(str(repo_root.resolve()))
    repo_name = repo_root.name.casefold()

    if repo_path and repo_path in normalized_status:
        return True

    return f"({repo_name} - visual studio code)" in normalized_status


def maybe_reload_vscode_window(repo_root: Path) -> None:
    code_bin = locate_vscode_cli()
    if not code_bin:
        print("Skipping VS Code reload: VS Code CLI is not available in PATH.")
        return

    if not _is_repo_window_open_in_vscode(code_bin, repo_root):
        print("Skipping VS Code reload: no open VS Code window found for this repository.")
        return

    reload_command = [
        code_bin,
        "--folder-uri",
        repo_root.resolve().as_uri(),
        "--reuse-window",
        "--command",
        "workbench.action.reloadWindow",
    ]
    result = subprocess.run(
        reload_command,
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    if result.returncode == 0:
        print("Triggered VS Code window reload for this repository.")
        return

    stderr = _as_text(result.stderr).strip()
    if stderr:
        print(f"VS Code reload request failed: {stderr}")
    else:
        print("VS Code reload request failed.")


def _bd_init_help_text(bd_bin: str, repo_root: Path) -> str:
    result = subprocess.run(
        [bd_bin, "init", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    stdout = _as_text(result.stdout)
    stderr = _as_text(result.stderr)
    return "\n".join(part for part in (stdout, stderr) if part)


def _build_bd_init_commands(bd_bin: str, help_text: str) -> list[list[str]]:
    base_command = [bd_bin, "init"]

    if "--skip-agents" in help_text:
        base_command.append("--skip-agents")
    if "--non-interactive" in help_text:
        base_command.append("--non-interactive")

    candidate_commands: list[list[str]] = []
    if "--server" in help_text:
        candidate_commands.append([*base_command, "--server"])
    elif "--mode" in help_text:
        candidate_commands.append([*base_command, "--mode", "server"])

    candidate_commands.append(base_command)

    unique_commands: list[list[str]] = []
    for command in candidate_commands:
        if command not in unique_commands:
            unique_commands.append(command)
    return unique_commands


def _run_bd_init_with_fallback(commands: list[list[str]], repo_root: Path) -> None:
    failures: list[str] = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=False,
            check=False,
        )
        if result.returncode == 0:
            return

        stdout = _as_text(result.stdout)
        stderr = _as_text(result.stderr)
        output = "\n".join(part.strip() for part in (stdout, stderr) if part and part.strip())
        if not output:
            output = "(no output)"
        failures.append(f"$ {' '.join(command)}\n{output}")

    details = "\n\n---\n\n".join(failures)
    raise RuntimeError(f"All Beads init commands failed:\n\n{details}")


def _is_beads_initialized(repo_root: Path) -> bool:
    bd_bin = locate_bd(repo_root)
    if not bd_bin:
        return False

    result = subprocess.run(
        [bd_bin, "info", "--json"],
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    return result.returncode == 0


def maybe_init_beads(repo_root: Path) -> None:
    if _is_beads_initialized(repo_root):
        return

    bd_bin = locate_bd(repo_root)
    if not bd_bin:
        print("Skipping 'bd init': bd is not available yet.")
        return

    help_text = _bd_init_help_text(bd_bin, repo_root)
    commands = _build_bd_init_commands(bd_bin, help_text)
    preferred = " ".join(commands[0])
    print(f"Initializing Beads with '{preferred}'...")
    _run_bd_init_with_fallback(commands, repo_root)


def derive_issue_prefix(repo_root: Path) -> str:
    raw_name = repo_root.name.strip().lower()
    if not raw_name:
        return "project"

    normalized = ISSUE_PREFIX_SANITIZE_PATTERN.sub("-", raw_name)
    normalized = normalized.strip("._-")
    if not normalized:
        return "project"

    return normalized


def ensure_repo_issue_prefix(repo_root: Path) -> None:
    bd_bin = locate_bd(repo_root)
    if not bd_bin:
        print("Skipping issue prefix configuration: bd is not available yet.")
        return

    desired_prefix = derive_issue_prefix(repo_root)
    print(f"Setting Beads issue prefix to repository name: {desired_prefix}")

    configured_keys: list[str] = []
    for key in ("issue_prefix", "issue-prefix", "id.prefix"):
        result = subprocess.run(
            [bd_bin, "config", "set", key, desired_prefix],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode == 0:
            configured_keys.append(key)

    if configured_keys:
        configured_keys_text = ", ".join(configured_keys)
        print(f"Configured Beads issue prefix: {desired_prefix} ({configured_keys_text})")
        return

    raise RuntimeError(
        "Failed to set Beads issue prefix. Run: bd config set issue_prefix <repo-name>"
    )


def _is_git_repository(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    return result.returncode == 0 and _as_text(result.stdout).strip() == "true"


def report_setup_artifact_changes(repo_root: Path) -> None:
    if not _is_git_repository(repo_root):
        return

    result = subprocess.run(
        ["git", "status", "--short", "--", ".gitignore", ".beads/hooks"],
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    if result.returncode != 0:
        return

    output = _as_text(result.stdout)
    changes = [line.strip() for line in output.splitlines() if line.strip()]
    if not changes:
        return

    print("Bootstrap changed tracked setup artifacts:")
    for change in changes:
        print(f"  {change}")

    print("Commit setup artifacts in one commit:")
    print("  git add .gitignore .beads/hooks")
    print('  git commit -m "chore(setup): record beads bootstrap artifacts (bd-setup)"')


def print_post_init_workflow_hint(repo_root: Path) -> None:
    if not _is_beads_initialized(repo_root):
        return

    print("Next required step before implementation:")
    print("  Use prompt: .github/prompts/start-work-session.prompt.md")
    print("If no bead is ready, create one with full description and claim it:")
    print('  bd create "Describe task" --description "Goal + criteria" -t task -p 2 --json')
    print("  bd backup export-git")
    print("  bd update <id> --claim --json")
    print("  bd backup export-git")
    print("Then draft a 3-7 step implementation plan before coding.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize development environment")
    parser.add_argument(
        "--python",
        default=None,
        help="Optional Python interpreter path used to create .venv",
    )
    parser.add_argument(
        "--force-recreate-venv",
        action="store_true",
        help="Delete and recreate .venv",
    )
    parser.add_argument(
        "--skip-beads",
        action="store_true",
        help="Skip Beads bootstrap",
    )
    parser.add_argument(
        "--update-tools",
        action="store_true",
        help="Offer/update Beads and Dolt versions during bootstrap",
    )
    parser.add_argument(
        "--skip-hooks",
        action="store_true",
        help="Skip git hook installation",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip running validate.py --fast",
    )
    parser.add_argument(
        "--skip-node-tools",
        action="store_true",
        help="Skip installing Node-based tooling (markdown quality checks)",
    )
    parser.add_argument(
        "--no-auto-install-tools",
        action="store_true",
        help="Disable automatic installation attempts for missing Python/Node toolchains",
    )
    parser.add_argument(
        "--upgrade-pip",
        action="store_true",
        help="Upgrade pip in .venv before installing dependencies",
    )
    parser.add_argument(
        "--yes-to-all",
        action="store_true",
        help="Kept for compatibility; initialization is already non-interactive",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    auto_install_missing = not args.no_auto_install_tools

    print("=== Initialize Development Environment ===")
    if args.yes_to_all:
        print("--yes-to-all is now default behavior (non-interactive setup).")

    python_bin = resolve_python_interpreter(
        requested_python=args.python,
        repo_root=repo_root,
        auto_install_missing=auto_install_missing,
    )
    print(f"Using Python interpreter: {python_bin}")

    interpreter = ensure_venv(
        repo_root=repo_root,
        python_bin=python_bin,
        recreate=args.force_recreate_venv,
    )

    ensure_min_python_version(interpreter, repo_root)
    install_requirements(repo_root, interpreter, upgrade_pip=args.upgrade_pip)
    install_node_dependencies(
        repo_root,
        skip_node_tools=args.skip_node_tools,
        auto_install_missing=auto_install_missing,
    )

    if not args.skip_beads:
        bootstrap_cmd = [str(interpreter), "scripts/bootstrap_beads.py", "--yes-to-all"]
        if args.update_tools:
            bootstrap_cmd.append("--update-tools")
        run(bootstrap_cmd, cwd=repo_root)
        maybe_init_beads(repo_root)
        ensure_repo_issue_prefix(repo_root)

    if not args.skip_hooks and (repo_root / "install_hooks.py").exists():
        run([str(interpreter), "install_hooks.py", "--force"], cwd=repo_root)

    if args.skip_node_tools and not args.skip_validate:
        print("Skipping fast validation because --skip-node-tools was set.")
    elif not args.skip_validate and (repo_root / "validate.py").exists():
        run([str(interpreter), "validate.py", "--fast"], cwd=repo_root)

    report_setup_artifact_changes(repo_root)
    print_post_init_workflow_hint(repo_root)
    maybe_reload_vscode_window(repo_root)

    print("Environment initialization complete.")
    print(
        "If VS Code did not reload automatically, restart VS Code now so "
        "extensions and tooling load correctly."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
