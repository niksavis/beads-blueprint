#!/usr/bin/env python3
"""Repository quality gate.

Modes:
- python validate.py             -> tests-focused gate (pre-push default)
- python validate.py --commit    -> staged python lint + typing
- python validate.py --fast      -> quick lint + typing
- python validate.py --full      -> lint + typing + security + dependency audit + tests
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
VENV_BIN = ROOT / ".venv" / ("Scripts" if platform.system() == "Windows" else "bin")
PYTHON = VENV_BIN / ("python.exe" if platform.system() == "Windows" else "python")


def run_check(label: str, command: list[str]) -> int:
    print(f"\n[validate] {label}")
    result = subprocess.run(command, cwd=ROOT)
    status = "OK" if result.returncode == 0 else "FAIL"
    print(f"[validate] {label}: {status}")
    return result.returncode


def tool_path(name: str) -> str:
    candidate = VENV_BIN / (f"{name}.exe" if platform.system() == "Windows" else name)
    if candidate.exists():
        return str(candidate)
    resolved = shutil.which(name)
    if not resolved:
        raise FileNotFoundError(f"Tool not found: {name}")
    return resolved


def staged_files(ext: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.endswith(ext)]


def staged_python_files() -> list[str]:
    return staged_files(".py")


def staged_markdown_files() -> list[str]:
    return staged_files(".md")


def node_bin_path(name: str) -> str:
    ext = ".cmd" if platform.system() == "Windows" else ""
    candidate = ROOT / "node_modules" / ".bin" / f"{name}{ext}"
    if candidate.exists():
        return str(candidate)
    resolved = shutil.which(name)
    if not resolved:
        raise FileNotFoundError(f"Node tool not found: {name}. Run: npm install")
    return resolved


def run_ruff(files: list[str] | None = None) -> int:
    args = [tool_path("ruff"), "check"] + (files if files else ["."])
    return run_check("ruff", args)


def run_ruff_format(files: list[str] | None = None) -> int:
    args = [tool_path("ruff"), "format", "--check"] + (files if files else ["."])
    return run_check("ruff-format", args)


def run_pyright(paths: list[str] | None = None) -> int:
    args = [tool_path("pyright")]
    args += paths if paths else ["."]
    return run_check("pyright", args)


def run_bandit() -> int:
    return run_check("bandit", [tool_path("bandit"), "-r", ".", "-c", "pyproject.toml"])


def run_pip_audit() -> int:
    return run_check("pip-audit", [tool_path("pip-audit"), "-r", "requirements.txt"])


def run_markdownlint(files: list[str] | None = None) -> int:
    try:
        cli = node_bin_path("markdownlint-cli2")
    except FileNotFoundError as e:
        print(f"\n[validate] markdownlint: SKIP ({e})")
        return 0
    if files is not None:
        if not files:
            print("\n[validate] markdownlint: SKIP (no staged Markdown files)")
            return 0
        return run_check("markdownlint", [cli] + files)
    return run_check("markdownlint", [cli, "**/*.md"])


def run_pytest() -> int:
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        print("\n[validate] pytest: SKIP (no tests directory)")
        return 0
    return run_check("pytest", [tool_path("pytest"), "-q"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repository quality gate")
    parser.add_argument("--commit", action="store_true", help="Validate staged Python files")
    parser.add_argument("--fast", action="store_true", help="Run quick lint + type checks")
    parser.add_argument("--full", action="store_true", help="Run full quality suite")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not PYTHON.exists() and not shutil.which("ruff"):
        print(f"[validate] ERROR: missing virtual environment: {PYTHON}")
        print("[validate] Run: python scripts/initialize_environment.py")
        return 1

    failures: list[str] = []

    if args.commit:
        staged_py = staged_python_files()
        staged_md = staged_markdown_files()
        if not staged_py and not staged_md:
            print("[validate] No staged Python or Markdown files.")
            return 0
        checks = []
        if staged_py:
            checks += [
                ("ruff", run_ruff(staged_py)),
                ("ruff-format", run_ruff_format(staged_py)),
                ("pyright", run_pyright(staged_py)),
            ]
        if staged_md:
            checks += [("markdownlint", run_markdownlint(staged_md))]
    elif args.full:
        checks = [
            ("ruff", run_ruff()),
            ("ruff-format", run_ruff_format()),
            ("pyright", run_pyright()),
            ("markdownlint", run_markdownlint()),
            ("bandit", run_bandit()),
            ("pip-audit", run_pip_audit()),
            ("pytest", run_pytest()),
        ]
    elif args.fast:
        checks = [
            ("ruff", run_ruff()),
            ("ruff-format", run_ruff_format()),
            ("pyright", run_pyright()),
            ("markdownlint", run_markdownlint()),
        ]
    else:
        checks = [("pytest", run_pytest())]

    for name, code in checks:
        if code != 0:
            failures.append(name)

    print("\n" + "=" * 60)
    if failures:
        print(f"[validate] FAILED: {', '.join(failures)}")
        return 1

    mode = "commit" if args.commit else "full" if args.full else "fast" if args.fast else "push"
    print(f"[validate] ALL CHECKS PASSED (mode: {mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
