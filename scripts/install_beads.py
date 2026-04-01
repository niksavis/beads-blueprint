#!/usr/bin/env python3
"""Install Beads and Dolt binaries for local development.

Windows defaults:
- Beads: %LOCALAPPDATA%\\Programs\\bd\\bd.exe
- Dolt:  %LOCALAPPDATA%\\Programs\\dolt\\dolt.exe

This script installs missing tools, supports optional upgrades when tools
already exist, and ensures install directories are present in the user PATH
on Windows.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

if platform.system() == "Windows":
    import ctypes
    import winreg
else:
    ctypes = None
    winreg = None

BEADS_GITHUB_API = "https://api.github.com/repos/gastownhall/beads/releases"
DOLT_GITHUB_API = "https://api.github.com/repos/dolthub/dolt/releases"
USER_AGENT = "beads-blueprint-bootstrap"
DEFAULT_BEADS_VERSION = "0.63.3"


def detect_platform() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "darwin"
    if system == "linux":
        return "linux"
    raise RuntimeError(f"Unsupported operating system: {system}")


def detect_architecture() -> str:
    machine = platform.machine().lower()
    aliases = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    if machine in aliases:
        return aliases[machine]
    raise RuntimeError(f"Unsupported architecture: {machine}")


def request_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_release(api_base: str, version: str | None) -> dict:
    if version:
        normalized = version[1:] if version.startswith("v") else version
        for candidate in (f"v{normalized}", normalized):
            url = f"{api_base}/tags/{candidate}"
            try:
                return request_json(url)
            except urllib.error.HTTPError:
                continue
        raise RuntimeError(f"Unable to resolve release for version: {version}")
    return request_json(f"{api_base}/latest")


def prompt_yes(message: str, assume_yes: bool, default: bool = False) -> bool:
    if assume_yes:
        return default
    suffix = "[Y/n]" if default else "[y/N]"
    reply = input(f"{message} {suffix}: ").strip().lower()
    if not reply:
        return default
    return reply in {"y", "yes"}


def default_install_dir(tool_name: str, platform_name: str) -> Path:
    if platform_name == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA is not set on this system")
        return Path(local_app_data) / "Programs" / tool_name
    return Path.home() / ".local" / "programs" / tool_name


def release_version(release: dict) -> str:
    tag = str(release.get("tag_name", "")).strip()
    return tag[1:] if tag.startswith("v") else tag


def find_beads_asset(release: dict, platform_name: str, arch_name: str) -> tuple[str, str]:
    version = release_version(release)
    extension = "zip" if platform_name == "windows" else "tar.gz"
    arch_tokens = [arch_name]
    if arch_name == "amd64":
        arch_tokens.append("x86_64")
    expected = [f"beads_{version}_{platform_name}_{token}.{extension}" for token in arch_tokens]

    assets = release.get("assets", [])
    for asset in assets:
        name = str(asset.get("name", ""))
        if name in expected and asset.get("browser_download_url"):
            return name, asset["browser_download_url"]

    for asset in assets:
        name = str(asset.get("name", ""))
        low = name.lower()
        if not asset.get("browser_download_url"):
            continue
        if low.endswith(extension) and "beads" in low and platform_name in low:
            if any(token in low for token in arch_tokens):
                return name, asset["browser_download_url"]

    raise RuntimeError(
        f"No matching Beads asset for {platform_name}-{arch_name} in release {version}"
    )


def find_dolt_asset(release: dict, platform_name: str, arch_name: str) -> tuple[str, str]:
    extension = "zip" if platform_name == "windows" else "tar.gz"
    arch_tokens = [arch_name]
    if arch_name == "amd64":
        arch_tokens.append("x86_64")
    expected = [f"dolt-{platform_name}-{token}.{extension}" for token in arch_tokens]

    assets = release.get("assets", [])
    for asset in assets:
        name = str(asset.get("name", ""))
        if name in expected and asset.get("browser_download_url"):
            return name, asset["browser_download_url"]

    for asset in assets:
        name = str(asset.get("name", ""))
        low = name.lower()
        if not asset.get("browser_download_url"):
            continue
        if low.endswith(extension) and low.startswith("dolt-") and platform_name in low:
            if any(token in low for token in arch_tokens):
                return name, asset["browser_download_url"]

    raise RuntimeError(f"No matching Dolt asset for {platform_name}-{arch_name}")


def download_to_temp(url: str, suffix: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_path = Path(tmp_file.name)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        tmp_path.write_bytes(response.read())
    return tmp_path


def _extract_single_binary(
    archive_path: Path,
    destination_dir: Path,
    executable_name: str,
    is_windows: bool,
) -> Path:
    temp_extract_dir = Path(tempfile.mkdtemp(prefix="beads-blueprint-extract-"))

    if archive_path.name.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(temp_extract_dir)
    else:
        with tarfile.open(archive_path) as tf:
            tf.extractall(temp_extract_dir)

    candidates = list(temp_extract_dir.rglob(executable_name))
    if not candidates:
        raise RuntimeError(f"Could not find {executable_name} in downloaded archive")

    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / executable_name
    shutil.copy2(candidates[0], destination)

    for item in destination_dir.iterdir():
        if item == destination:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    if not is_windows:
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    shutil.rmtree(temp_extract_dir, ignore_errors=True)
    return destination


def _normalize_win_path(value: str) -> str:
    return value.strip().rstrip("\\/").lower()


def ensure_windows_user_path(entries: list[Path]) -> list[Path]:
    if winreg is None or ctypes is None:
        return []

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
        try:
            current_path, path_type = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path, path_type = "", winreg.REG_EXPAND_SZ

    parts = [p for p in str(current_path).split(";") if p.strip()]
    normalized = {_normalize_win_path(p) for p in parts}
    added: list[Path] = []

    for entry in entries:
        entry_str = str(entry)
        if _normalize_win_path(entry_str) in normalized:
            continue
        parts.append(entry_str)
        normalized.add(_normalize_win_path(entry_str))
        added.append(entry)

    if added:
        new_path = ";".join(parts)
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, "Path", 0, path_type, new_path)

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            None,
        )

        os.environ["PATH"] = f"{new_path};{os.environ.get('PATH', '')}"

    return added


def install_beads_binary(
    platform_name: str,
    arch_name: str,
    install_dir: Path,
    version: str,
) -> Path:
    release = resolve_release(BEADS_GITHUB_API, version)
    asset_name, asset_url = find_beads_asset(release, platform_name, arch_name)
    suffix = ".zip" if platform_name == "windows" else ".tar.gz"
    archive = download_to_temp(asset_url, suffix)
    try:
        executable_name = "bd.exe" if platform_name == "windows" else "bd"
        destination = _extract_single_binary(
            archive,
            install_dir,
            executable_name,
            is_windows=platform_name == "windows",
        )
        print(f"Installed Beads {release_version(release)} from asset: {asset_name}")
        print(f"Beads binary: {destination}")
        return destination
    finally:
        if archive.exists():
            archive.unlink()


def install_dolt_binary(
    platform_name: str,
    arch_name: str,
    install_dir: Path,
    version: str | None,
) -> Path:
    release = resolve_release(DOLT_GITHUB_API, version)
    asset_name, asset_url = find_dolt_asset(release, platform_name, arch_name)
    suffix = ".zip" if platform_name == "windows" else ".tar.gz"
    archive = download_to_temp(asset_url, suffix)
    try:
        executable_name = "dolt.exe" if platform_name == "windows" else "dolt"
        destination = _extract_single_binary(
            archive,
            install_dir,
            executable_name,
            is_windows=platform_name == "windows",
        )
        print(f"Installed Dolt {release_version(release)} from asset: {asset_name}")
        print(f"Dolt binary: {destination}")
        return destination
    finally:
        if archive.exists():
            archive.unlink()


def ensure_beads_and_dolt(
    *,
    force: bool = False,
    beads_version: str = DEFAULT_BEADS_VERSION,
    dolt_version: str | None = None,
    assume_yes: bool = False,
    update_existing: bool = False,
) -> dict[str, str | bool]:
    platform_name = detect_platform()
    arch_name = detect_architecture()

    bd_on_path = shutil.which("bd")
    dolt_on_path = shutil.which("dolt")

    should_update = update_existing
    if bd_on_path and dolt_on_path and not (force or update_existing):
        should_update = prompt_yes(
            "bd and dolt are already available. Update to requested versions now?",
            assume_yes=assume_yes,
            default=False,
        )

    install_bd = force or not bd_on_path or should_update
    install_dolt = force or not dolt_on_path or should_update

    bd_dir = default_install_dir("bd", platform_name)
    dolt_dir = default_install_dir("dolt", platform_name)
    bd_binary = bd_on_path or ""
    dolt_binary = dolt_on_path or ""

    if install_bd:
        bd_binary = str(install_beads_binary(platform_name, arch_name, bd_dir, beads_version))
    else:
        print(f"Using existing bd from PATH: {bd_on_path}")

    if install_dolt:
        dolt_binary = str(install_dolt_binary(platform_name, arch_name, dolt_dir, dolt_version))
    else:
        print(f"Using existing dolt from PATH: {dolt_on_path}")

    added_path_entries: list[str] = []
    if platform_name == "windows":
        path_candidates = []
        if (bd_dir / "bd.exe").exists() or install_bd:
            path_candidates.append(bd_dir)
        if (dolt_dir / "dolt.exe").exists() or install_dolt:
            path_candidates.append(dolt_dir)
        added = ensure_windows_user_path(path_candidates)
        if added:
            added_path_entries = [str(p) for p in added]
            print("Added directories to user PATH:")
            for path in added_path_entries:
                print(f"  - {path}")
            print("Restart VS Code and open a new terminal session to reload PATH.")

    return {
        "bd_binary": bd_binary,
        "dolt_binary": dolt_binary,
        "installed_bd": install_bd,
        "installed_dolt": install_dolt,
        "updated_existing": should_update,
        "added_path_entries": ",".join(added_path_entries),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install or update Beads + Dolt toolchain")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstall even if tools are already available",
    )
    parser.add_argument(
        "--beads-version",
        default=DEFAULT_BEADS_VERSION,
        help="Beads version tag (default: v0.63.3)",
    )
    parser.add_argument(
        "--dolt-version",
        help="Optional Dolt version tag (defaults to latest)",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update tools even when both bd and dolt are already available",
    )
    parser.add_argument(
        "--yes-to-all",
        action="store_true",
        help="Auto-answer prompts with defaults",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_beads_and_dolt(
        force=args.force,
        beads_version=args.beads_version,
        dolt_version=args.dolt_version,
        assume_yes=args.yes_to_all,
        update_existing=args.update_existing,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
