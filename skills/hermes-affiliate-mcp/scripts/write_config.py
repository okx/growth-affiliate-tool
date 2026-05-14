#!/usr/bin/env python3
"""Inject the current access_token into ~/.hermes/config.yaml.

Idempotent: maintains a single managed block delimited by BLOCK_BEGIN/END
markers. Re-running replaces the previous block in-place. Anything outside
the markers — including the user's other mcp_servers entries — is preserved
exactly (whitespace, comments, ordering).

Strategy:
  1. Read token.json -> access_token.
  2. Read config.yaml.
  3. If config.yaml has an existing managed block, replace it.
     Otherwise, append a fresh mcp_servers entry under a new managed block
     at the end of the file (Hermes will merge with any top-level
     mcp_servers: key already in the file? No — YAML disallows duplicate
     top-level keys. We detect this and bail with a clear message.)

Hermes hot-reloads MCP servers when config.yaml changes, so the new token
takes effect within seconds with no restart.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _common import (
    BLOCK_BEGIN,
    BLOCK_END,
    HERMES_CONFIG,
    RESOURCE,
    SERVER_NAME,
    die,
    read_json,
)


MANAGED_BODY_TEMPLATE = """{begin}
# Auto-managed by the okx-affiliate-mcp skill. Re-run scripts/write_config.py
# (or scripts/refresh.py) to update the bearer token. Do not edit by hand.
mcp_servers:
  {server_name}:
    url: "{url}"
    headers:
      Authorization: "Bearer {token}"
    timeout: 120
    connect_timeout: 60
{end}
"""


def _existing_top_level_mcp_servers(text: str) -> bool:
    """True if config.yaml already has an unmanaged top-level 'mcp_servers:' key."""
    inside_block = False
    for raw in text.splitlines():
        if raw.strip() == BLOCK_BEGIN:
            inside_block = True
            continue
        if raw.strip() == BLOCK_END:
            inside_block = False
            continue
        if inside_block:
            continue
        # Top-level key = starts at column 0, no leading whitespace, ends with ':'
        if raw.startswith("mcp_servers:") or raw.startswith("mcp_servers ") or raw.rstrip() == "mcp_servers:":
            return True
    return False


def _replace_or_append(text: str, block: str) -> str:
    begin_idx = text.find(BLOCK_BEGIN)
    end_idx = text.find(BLOCK_END)
    if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
        # Replace existing block (include trailing newline of END marker).
        end_line_end = text.find("\n", end_idx)
        if end_line_end == -1:
            end_line_end = len(text)
        return text[:begin_idx] + block.rstrip() + text[end_line_end:]
    # Append. Ensure exactly one blank line before our block.
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    return text + block


def main() -> int:
    tok = read_json("token.json")
    access_token = tok.get("access_token")
    if not access_token:
        die("token.json has no access_token; run exchange.py or refresh.py first")

    config_path: Path = HERMES_CONFIG
    if not config_path.exists():
        # Create a minimal file so Hermes picks it up.
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("# Hermes Agent config\n")

    text = config_path.read_text()

    if _existing_top_level_mcp_servers(text):
        die(
            "Your ~/.hermes/config.yaml already has a top-level 'mcp_servers:' key "
            "outside the managed block. YAML cannot have duplicate top-level keys. "
            "Move your existing mcp_servers entries into the managed block, or "
            "merge manually:\n\n"
            f"  mcp_servers:\n"
            f"    {SERVER_NAME}:\n"
            f"      url: \"{RESOURCE}\"\n"
            f"      headers:\n"
            f"        Authorization: \"Bearer <token from {tok and 'token.json'}>\"\n"
        )

    block = MANAGED_BODY_TEMPLATE.format(
        begin=BLOCK_BEGIN,
        end=BLOCK_END,
        server_name=SERVER_NAME,
        url=RESOURCE,
        token=access_token,
    )
    new_text = _replace_or_append(text, block)

    if new_text == text:
        print(f"config.yaml already up to date: {config_path}")
        return 0

    # Write atomically to avoid Hermes seeing a half-written file mid-reload.
    tmp = config_path.with_suffix(".yaml.tmp")
    tmp.write_text(new_text)
    tmp.replace(config_path)

    print(f"✓ wrote managed mcp_servers.{SERVER_NAME} block to {config_path}")
    print("  Hermes will hot-reload MCP within a few seconds; no restart needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
