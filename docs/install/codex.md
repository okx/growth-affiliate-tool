# Install on Codex CLI

[← Back to install index](../../README.md#quick-start)

OpenAI Codex CLI has native support for remote HTTP MCP servers with OAuth.

## Prerequisites

- [Codex CLI](https://github.com/openai/codex) installed
- An OKX account that is enrolled as an **Affiliate**

## Step 1 — Register the MCP

Edit Codex's MCP configuration file. The path depends on your OS:

| OS              | Config path                                              |
| --------------- | -------------------------------------------------------- |
| macOS / Linux   | `~/.codex/mcp.json` *(or `~/.config/codex/mcp.json`)*    |
| Windows         | `%USERPROFILE%\.codex\mcp.json`                          |

> Refer to your Codex version's docs for the canonical path — the file format below is the
> standard MCP config used across most clients.

Add the server entry:

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

If the file already lists other MCPs, just add the `growth-affiliate-pro-tools` key under
`mcpServers`.

## Step 2 — Restart Codex and trigger OAuth

Restart your Codex session. Then ask Codex to authenticate the new MCP — the exact phrasing
depends on your Codex version, but something like:

> *Connect / authenticate the growth-affiliate-pro-tools MCP.*

Codex will open a browser and walk you through OAuth. The four-step flow is identical to the
Claude Code flow — see [`claude-code.md`](claude-code.md#authentication) for the screenshots
and scope guidance:

1. `/mcp` (or Codex equivalent) → browser opens
2. Sign in to your OKX **Affiliate** account
3. Grant scope: **Live Trading → Read-only ON**, everything else OFF
4. Confirmation: *Authentication successful*

## Step 3 — Smoke-test

Ask Codex:

> *Show me my affiliate performance.*

It should call `okx-affiliate-performance-summary` and return numbers.

## Troubleshooting

Same patterns as Claude Code — see [`claude-code.md#troubleshooting`](claude-code.md#troubleshooting)
or the project [FAQ](../faq.md).

If your Codex version uses a different MCP config schema (some early versions used a
TOML-based format), check the latest Codex documentation and adapt the field names. The
required values are always:

- transport / type: `http`
- URL: `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
