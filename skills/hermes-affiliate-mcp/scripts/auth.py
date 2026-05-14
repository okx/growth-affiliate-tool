#!/usr/bin/env python3
"""Step 2: Build the authorize URL for the user.

Generates PKCE verifier/challenge + state, persists them to pkce.json, and prints
the authorize URL (also saved to auth_url.txt).

The user opens this URL in a browser, logs in to OKX, approves, and gets
redirected to http://localhost:8787/callback?code=...&state=...
The redirect is expected to fail to load (no local server); the agent only needs
the `code` and `state` from the URL bar to run exchange.py.
"""
from __future__ import annotations

import base64
import hashlib
import os
import sys
from urllib.parse import urlencode

from _common import (
    AUTHORIZE_URL,
    DEFAULT_SCOPE,
    REDIRECT_URI,
    RESOURCE,
    die,
    read_json,
    write_json,
    file,
)


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def main() -> None:
    client = read_json("client.json")
    client_id = client.get("client_id")
    if not client_id:
        die("client.json missing client_id; re-run register.py")

    # Optional: scope override via CLI arg (e.g. "live:read live:trade")
    scope = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCOPE

    code_verifier = _b64url(os.urandom(40))
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode("utf-8")).digest())
    state = _b64url(os.urandom(16))

    write_json(
        "pkce.json",
        {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "state": state,
            "scope": scope,
            "client_id": client_id,
        },
    )

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "flow": "code",  # OKX-specific: required to render the OAuth approval UI
        "resource": RESOURCE,
    }
    url = f"{AUTHORIZE_URL}?{urlencode(params)}"

    out = file("auth_url.txt")
    out.write_text(url)

    print(url)
    print(f"\n(also saved to {out})")
    print(
        "\nReminder for the agent: when you forward this URL to the user, also tell them\n"
        "that after clicking Authorize the browser will show a BLANK / 'site can't be reached'\n"
        "page at localhost:8787 \u2014 that is the success state. They should copy the FULL URL\n"
        "from the address bar and paste it back. See reference/blank-callback-page.md."
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
