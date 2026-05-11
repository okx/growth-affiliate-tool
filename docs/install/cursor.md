# Install on Cursor

[← Back to install index](../../README.md#quick-start)

Cursor supports remote HTTP MCP servers with native OAuth via project-level or user-level
configuration files.

## Prerequisites

- Cursor installed
- An OKX account that is enrolled as an **Affiliate**

## Step 1 — Register the MCP

Pick **one** of:

### Project-level (recommended for team sharing)

Add to `.cursor/mcp.json` in your project root:

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

### User-level (applies to all projects)

Add to `~/.cursor/mcp.json`:

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

If the file already exists with other MCPs, just add the `growth-affiliate-pro-tools` key
under `mcpServers`.

## Step 2 — Reload and authenticate

In Cursor: open the command palette → *Reload MCP servers* (or restart Cursor). Cursor will
detect the new server and prompt for OAuth.

Walk through the four OAuth steps — see [`claude-code.md#authentication`](claude-code.md#authentication)
for the screenshots and scope guidance:

1. Browser opens automatically
2. Sign in to your OKX **Affiliate** account
3. Grant scope: **Live Trading → Read-only ON**, everything else OFF
4. Confirmation appears in Cursor

## Step 3 — Smoke-test

In a Cursor chat:

> *Show me my affiliate performance.*

Expect a table with invitees, deposits, volume, and commission.

## Troubleshooting

Same patterns as Claude Code — see [`claude-code.md#troubleshooting`](claude-code.md#troubleshooting)
or the project [FAQ](../faq.md).
