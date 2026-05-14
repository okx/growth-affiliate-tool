#!/usr/bin/env python3
"""End-to-end refresh: refresh token + write to config.yaml.

This is the script you run from cron (or manually) once the install is
complete. It:

  1. Runs the standard OAuth refresh against OKX (refresh.py logic).
  2. Updates ~/.hermes/config.yaml with the new bearer token
     (write_config.py logic).

Exits 0 on success, non-zero on failure. Logs to stderr so cron mails
problems but stays quiet on success.

If the refresh_token has died, you'll need to re-run the full auth flow:
    python3 scripts/auth.py
    # open the URL, paste the callback URL back
    python3 scripts/exchange.py "<callback-url>"
    python3 scripts/write_config.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str) -> int:
    proc = subprocess.run(
        [sys.executable, str(HERE / script)],
        cwd=str(HERE),
    )
    return proc.returncode


def main() -> int:
    rc = run("refresh.py")
    if rc != 0:
        print(
            "refresh.py failed. The refresh_token may have expired — re-run "
            "auth.py + exchange.py + write_config.py to do a fresh login.",
            file=sys.stderr,
        )
        return rc

    rc = run("write_config.py")
    if rc != 0:
        print("write_config.py failed; token.json is fresh but config.yaml not updated.", file=sys.stderr)
        return rc

    return 0


if __name__ == "__main__":
    sys.exit(main())
