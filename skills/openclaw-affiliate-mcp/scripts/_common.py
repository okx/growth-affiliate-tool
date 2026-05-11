"""Shared helpers for okx-affiliate-mcp scripts.

Stdlib only — no third-party deps so the skill works on any Python 3.8+.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Where credentials live. User-level, cross-workspace.
DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/okx-affiliate-mcp"))

# OKX-specific endpoints (see reference/oauth-endpoints.md).
REGISTER_URL = "https://www.okx.com/api/v5/mcp/auth/register"
AUTHORIZE_URL = "https://www.okx.com/account/oauth"
TOKEN_URL = "https://www.okx.com/api/v5/mcp/auth/token"

# The MCP we are authorizing against. Required as `resource` on every OAuth call.
RESOURCE = "https://www.okx.com/api/v1/mcp/growth-affiliate-mcp"

# Local redirect target. We do NOT actually run a server on this port; the user
# pastes the redirected URL back to the agent. The value just has to match what
# was registered via DCR and what is sent on every authorize/token call.
REDIRECT_URI = "http://localhost:8787/callback"

# Default scope. Note: the access token is allowed to upgrade beyond what we
# register; OKX returns the full granted scope on the token response.
DEFAULT_SCOPE = "live:read"

# OKX sits behind Cloudflare; the default urllib UA (`Python-urllib/3.x`) gets
# served HTTP 403 with body `error code: 1010`. Any browser-ish UA works.
_USER_AGENT = "openclaw-affiliate-skill/1.0"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def file(name: str) -> Path:
    return DATA_DIR / name


def read_json(name: str) -> dict:
    path = file(name)
    if not path.exists():
        die(f"Missing {path}. Run earlier step first.")
    with path.open() as f:
        return json.load(f)


def write_json(name: str, data: dict) -> Path:
    ensure_data_dir()
    path = file(name)
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    return path


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def now() -> int:
    return int(time.time())


def http_post_form(url: str, data: dict) -> tuple[int, dict | str]:
    """POST form-encoded body using stdlib only. Returns (status, parsed-json-or-text)."""
    from urllib import parse, request, error

    body = parse.urlencode(data).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw


def http_post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    """POST application/json body using stdlib only."""
    from urllib import request, error

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw
