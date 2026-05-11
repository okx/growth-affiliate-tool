#!/usr/bin/env python3
"""Step 3: Exchange the authorization code for tokens.

Usage:
    python3 exchange.py "<code>"
    python3 exchange.py "<full-callback-url>"   # also accepted

If a full URL is provided, both `code` and `state` are extracted and `state` is
verified against pkce.json (recommended).
"""
from __future__ import annotations

import sys
from urllib.parse import parse_qs, urlparse

from _common import (
    REDIRECT_URI,
    RESOURCE,
    TOKEN_URL,
    die,
    http_post_form,
    now,
    read_json,
    write_json,
)


def _parse_input(arg: str) -> tuple[str, str | None]:
    """Accept any of:
      - bare authorization code
      - full URL: http(s)://host/callback?code=...&state=...
      - schemeless URL: localhost:8787/callback?code=...&state=...
      - bare query: code=...&state=...
    """
    looks_like_url = (
        arg.startswith("http://")
        or arg.startswith("https://")
        or "?" in arg
        or arg.startswith("/")
        or arg.lower().startswith("localhost")
    )
    if not looks_like_url:
        return arg, None

    # Normalize so urlparse gives us a query component.
    if not (arg.startswith("http://") or arg.startswith("https://")):
        arg = "http://" + arg.lstrip("/")

    qs = parse_qs(urlparse(arg).query)
    code = (qs.get("code") or [None])[0]
    state = (qs.get("state") or [None])[0]
    if not code:
        die("Could not find ?code= in the URL you pasted.")
    return code, state


def main() -> None:
    if len(sys.argv) < 2:
        die("Usage: exchange.py <code-or-callback-url>")

    code, returned_state = _parse_input(sys.argv[1])

    pkce = read_json("pkce.json")
    client = read_json("client.json")

    if returned_state is not None and returned_state != pkce.get("state"):
        die(
            "state mismatch — refusing to exchange. "
            "The callback URL is for a different auth attempt; re-run auth.py."
        )

    data = {
        "grant_type": "authorization_code",
        "client_id": client["client_id"],
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "code_verifier": pkce["code_verifier"],
        "resource": RESOURCE,  # required, otherwise: invalid_grant: resource does not match
    }

    status, body = http_post_form(TOKEN_URL, data)
    if status != 200 or not isinstance(body, dict) or "access_token" not in body:
        die(f"Token exchange failed: HTTP {status}\n{body}")

    body["obtained_at"] = now()
    path = write_json("token.json", body)
    print(f"✓ access_token obtained (scope: {body.get('scope', '?')})")
    print(f"  expires_in={body.get('expires_in')}s  saved to {path}")


if __name__ == "__main__":
    sys.exit(main() or 0)
