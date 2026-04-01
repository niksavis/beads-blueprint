#!/usr/bin/env python3
"""Initialize local development environment for this template.

This script is intentionally Python-only so the same command works on
Windows, macOS, and Linux.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


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


def install_requirements(repo_root: Path, interpreter: Path) -> None:
    print("Installing Python dependencies...")
    run([str(interpreter), "-m", "pip", "install", "--upgrade", "pip"], cwd=repo_root)

    for filename in ("requirements.txt", "requirements-dev.txt"):
        file_path = repo_root / filename
        if file_path.exists():
            run([str(interpreter), "-m", "pip", "install", "-r", filename], cwd=repo_root)


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
        run([bd_bin, "init"], cwd=repo_root, check=False)


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
        "--yes-to-all",
        action="store_true",
        help="Auto-confirm interactive prompts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    print("=== Initialize Development Environment ===")
    interpreter = ensure_venv(
        repo_root=repo_root,
        python_bin=args.python,
        recreate=args.force_recreate_venv,
    )

    install_requirements(repo_root, interpreter)

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

    if not args.skip_validate and (repo_root / "validate.py").exists():
        run([str(interpreter), "validate.py", "--fast"], cwd=repo_root, check=False)

    print("Environment initialization complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
