# Install on Hermes

[← Back to install index](../../README.md#quick-start)

Hermes supports remote HTTP MCP servers with native OAuth.

## Prerequisites

- Hermes installed and configured
- An OKX account that is enrolled as an **Affiliate**

## Step 1 — Register the MCP

Edit Hermes's MCP configuration file (path varies by Hermes version — check your installation
docs; commonly `~/.hermes/mcp.json` or `~/.config/hermes/mcp.json`):

```json
{
  "mcpServers": {
    "growth-affiliate-pro-tools": {
      "type": "http",
      "url": "https://www.okx.com/api/v1/mcp/growth-affiliate-mcp"
    }
  }
}
```

If the file already exists with other MCP entries, just add the `growth-affiliate-pro-tools`
entry under `mcpServers`.

## Step 2 — Restart Hermes and authenticate

Restart your Hermes session, then trigger OAuth via Hermes's MCP auth command (typically
`/mcp` or an equivalent menu action).

The OAuth flow is identical to Claude Code — see
[`claude-code.md#authentication`](claude-code.md#authentication) for the four screenshots and
scope guidance:

1. Trigger OAuth → browser opens
2. Sign in to your OKX **Affiliate** account
3. Grant scope: **Live Trading → Read-only ON**, everything else OFF
4. Confirmation: *Authentication successful*

## Step 3 — Smoke-test

Ask Hermes:

> *Show me my affiliate performance.*

A non-empty response with commission and volume numbers means you are connected.

## Troubleshooting

See the [FAQ](../faq.md). Most issues map 1:1 with Claude Code — wrong OKX account, expired
tokens (~1 h lifetime), or `limit ≥ 99` on `okx-affiliate-invitee-list` (cap at `"95"`).
