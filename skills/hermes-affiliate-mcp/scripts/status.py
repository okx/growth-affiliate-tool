#!/usr/bin/env python3
"""Status — print a 1-line summary of install state. Used by the SKILL decision tree."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import DATA_DIR, file, now, token_expires_in


def main() -> int:
    if not DATA_DIR.exists():
        print("state: not_installed (no DATA_DIR)")
        return 0

    have_client = file("client.json").exists()
    have_token = file("token.json").exists()
    if not have_client:
        print("state: not_installed (no client.json — run register.py)")
        return 0
    if not have_token:
        print("state: registered_but_unauthed (have client.json, no token.json — run auth.py)")
        return 0

    secs = token_expires_in()
    if secs is None:
        print("state: token_malformed (re-run auth.py + exchange.py)")
        return 0

    if secs > 300:
        print(f"state: ok (token valid for {secs}s)")
    elif secs > 0:
        print(f"state: expiring_soon (token valid for {secs}s — run auto_refresh.py)")
    else:
        print(f"state: expired (token expired {-secs}s ago — run auto_refresh.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
