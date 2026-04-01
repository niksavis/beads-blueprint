#!/usr/bin/env python3
"""Session logger hook for GitHub Copilot Chat.

Reads JSON context from stdin and appends a JSONL entry to logs/copilot/session.log.
Invoked by .github/hooks/session-logger-lite/hooks.json for SessionStart and Stop
events.

Usage:
    python .github/hooks/scripts/session_logger.py session_start
    python .github/hooks/scripts/session_logger.py session_end
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"

    raw = sys.stdin.read()
    data: dict = {}
    with contextlib.suppress(json.JSONDecodeError, ValueError):
        data = json.loads(raw)

    ws_path = Path(data.get("cwd", os.getcwd()))
    log_dir = ws_path / "logs" / "copilot"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "session.log"

    if event == "session_start":
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "session_start",
            "cwd": str(ws_path),
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print("[session-logger-lite] session start logged.")

    elif event == "session_end":
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "session_end",
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print("[session-logger-lite] session end logged.")


if __name__ == "__main__":
    main()
