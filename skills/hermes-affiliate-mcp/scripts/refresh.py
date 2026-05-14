#!/usr/bin/env python3
"""Step 4: Refresh the access token.

Reads token.json + client.json, posts grant_type=refresh_token (with the
mandatory `resource` parameter), and overwrites token.json.

Exits non-zero on failure so callers can fall back to the auth.py flow.
"""
from __future__ import annotations

import sys

from _common import (
    RESOURCE,
    TOKEN_URL,
    die,
    http_post_form,
    now,
    read_json,
    write_json,
)


def main() -> int:
    tok = read_json("token.json")
    client = read_json("client.json")

    refresh_token = tok.get("refresh_token")
    if not refresh_token:
        die("token.json has no refresh_token; re-run auth.py + exchange.py")

    data = {
        "grant_type": "refresh_token",
        "client_id": client["client_id"],
        "refresh_token": refresh_token,
        "resource": RESOURCE,  # still required on refresh
    }

    status, body = http_post_form(TOKEN_URL, data)
    if status != 200 or not isinstance(body, dict) or "access_token" not in body:
        print(f"refresh failed: HTTP {status}\n{body}", file=sys.stderr)
        return 2  # caller should fall back to auth flow

    body["obtained_at"] = now()
    path = write_json("token.json", body)
    print(f"✓ refreshed; expires_in={body.get('expires_in')}s  saved to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
