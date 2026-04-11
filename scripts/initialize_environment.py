#!/usr/bin/env python3
"""Initialize local development environment for this template.

This script is intentionally Python-first so the same command works on
Windows, macOS, and Linux. Repository markdown quality tooling relies
on Node via npm.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON_VERSION = (3, 14)
PINNED_REQUIREMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[^\s]+(?:\s*;.+)?$"
)


def run(command: list[str], cwd: Path, check: bool = True) -> int:
    result = subprocess.run(command, cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    return result.returncode


def prompt_yes(message: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    value = input(f"{message} [y/N]: ").strip().lower()
    return value in {"y", "yes"}


def venv_python_path(repo_root: Path) -> Path:
    if sys.platform.startswith("win"):
        return repo_root / ".venv" / "Scripts" / "python.exe"
    return repo_root / ".venv" / "bin" / "python"


def python_version(python_bin: str | Path, cwd: Path) -> tuple[int, int, int]:
    code = "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"
    result = subprocess.run(
        [str(python_bin), "-c", code],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Unable to determine Python version for interpreter: {python_bin}")

    parts = result.stdout.strip().split(".")
    if len(parts) != 3:
        raise RuntimeError(f"Unexpected Python version output from interpreter: {python_bin}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def ensure_min_python_version(python_bin: str | Path, repo_root: Path) -> None:
    version = python_version(python_bin, repo_root)
    if version < MIN_PYTHON_VERSION:
        required = ".".join(str(part) for part in MIN_PYTHON_VERSION)
        actual = ".".join(str(part) for part in version)
        raise RuntimeError(f"Python {required}+ is required, but found {actual} at: {python_bin}")


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


def install_requirements(repo_root: Path, interpreter: Path, upgrade_pip: bool) -> None:
    print("Installing Python dependencies...")
    lockfiles = ("requirements.txt", "requirements-dev.txt")
    missing = [name for name in lockfiles if not (repo_root / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing lockfile(s): {joined}")

    if upgrade_pip:
        run([str(interpreter), "-m", "pip", "install", "--upgrade", "pip"], cwd=repo_root)

    for filename in lockfiles:
        ensure_pinned_lockfile(repo_root / filename)
        run(
            [str(interpreter), "-m", "pip", "install", "--require-virtualenv", "-r", filename],
            cwd=repo_root,
        )


def install_node_dependencies(repo_root: Path, skip_node_tools: bool) -> None:
    package_json = repo_root / "package.json"
    if skip_node_tools or not package_json.exists():
        return

    npm_bin = shutil.which("npm")
    if not npm_bin:
        raise RuntimeError(
            "npm is required for repository markdown lint tooling. "
            "Install Node.js 20+ and rerun, or pass --skip-node-tools."
        )

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


def maybe_init_beads(repo_root: Path, assume_yes: bool) -> None:
    if (repo_root / ".beads").exists():
        return

    bd_bin = locate_bd(repo_root)
    if not bd_bin:
        print("Skipping 'bd init': bd is not available yet.")
        return

    if prompt_yes("Initialize Beads now with 'bd init'?", assume_yes):
        run([bd_bin, "init"], cwd=repo_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize development environment")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter used to create .venv",
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
        "--upgrade-pip",
        action="store_true",
        help="Upgrade pip in .venv before installing dependencies",
    )
    parser.add_argument(
        "--yes-to-all",
        action="store_true",
        help="Auto-confirm interactive prompts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    print("=== Initialize Development Environment ===")
    ensure_min_python_version(args.python, repo_root)
    interpreter = ensure_venv(
        repo_root=repo_root,
        python_bin=args.python,
        recreate=args.force_recreate_venv,
    )

    ensure_min_python_version(interpreter, repo_root)
    install_requirements(repo_root, interpreter, upgrade_pip=args.upgrade_pip)
    install_node_dependencies(repo_root, skip_node_tools=args.skip_node_tools)

    if not args.skip_beads:
        bootstrap_cmd = [str(interpreter), "scripts/bootstrap_beads.py"]
        if args.yes_to_all:
            bootstrap_cmd.append("--yes-to-all")
        if args.update_tools:
            bootstrap_cmd.append("--update-tools")
        run(bootstrap_cmd, cwd=repo_root)
        maybe_init_beads(repo_root, args.yes_to_all)

    if not args.skip_hooks and (repo_root / "install_hooks.py").exists():
        run([str(interpreter), "install_hooks.py", "--force"], cwd=repo_root)

    if args.skip_node_tools and not args.skip_validate:
        print("Skipping fast validation because --skip-node-tools was set.")
    elif not args.skip_validate and (repo_root / "validate.py").exists():
        run([str(interpreter), "validate.py", "--fast"], cwd=repo_root)

    print("Environment initialization complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
