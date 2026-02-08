"""Generate build/version_info.txt from version.py."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VERSION_FILE = PROJECT_ROOT / "version.py"
OUTPUT_DIR = PROJECT_ROOT / "build"


def read_version() -> str:
    content = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in version.py")
    return match.group(1)


def write_version_info(version: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    info_path = OUTPUT_DIR / "version_info.txt"
    updater_path = OUTPUT_DIR / "version_info_updater.txt"

    info_path.write_text(f"Version={version}\n", encoding="utf-8")
    updater_path.write_text(f"UpdaterVersion={version}\n", encoding="utf-8")


def main() -> int:
    version = read_version()
    write_version_info(version)
    print(f"Wrote build/version_info.txt for {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
