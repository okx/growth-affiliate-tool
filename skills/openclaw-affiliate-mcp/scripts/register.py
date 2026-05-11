#!/usr/bin/env python3
"""Step 1: Register a Dynamic Client (DCR) with OKX.

One-shot per install. Writes ~/.openclaw/data/okx-affiliate-mcp/client.json.
Skip if client.json already exists (idempotent).
"""
from __future__ import annotations

import sys
from _common import (
    DEFAULT_SCOPE,
    REDIRECT_URI,
    REGISTER_URL,
    die,
    file,
    http_post_json,
    write_json,
)


def main() -> None:
    if file("client.json").exists():
        print(f"client.json already exists at {file('client.json')}; skipping registration.")
        return

    payload = {
        "client_name": "OpenClaw Affiliate MCP Client",
        "redirect_uris": [REDIRECT_URI],
        "scope": DEFAULT_SCOPE,
    }

    status, body = http_post_json(REGISTER_URL, payload)
    if status != 200 and status != 201:
        die(f"DCR failed: HTTP {status}\n{body}")

    if not isinstance(body, dict) or "client_id" not in body:
        die(f"DCR returned unexpected payload: {body}")

    path = write_json("client.json", body)
    print(f"✓ Registered client_id={body['client_id']}")
    print(f"  saved to {path}")


if __name__ == "__main__":
    sys.exit(main() or 0)
