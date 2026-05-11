# Install on a generic MCP client

[← Back to install index](../../README.md#quick-start)

If your client supports **remote HTTP MCP servers with native OAuth** (most modern MCP
clients do), this single config snippet is everything you need.

## The MCP entry

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

Drop it into whatever config file your client uses for MCP servers (commonly `mcp.json` or a
nested `mcpServers` block in a larger settings file).

## Configuration reference

| Field   | Value                                                   | Required | Notes                       |
| ------- | ------------------------------------------------------- | :------: | --------------------------- |
| `type`  | `http`                                                  | ✅       | Streamable HTTP transport   |
| `url`   | `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`   | ✅       | OKX-hosted endpoint         |

No `Authorization` header is needed in the config — your client handles OAuth itself the
first time the MCP is called.

## OAuth flow

Same four steps used by every native-OAuth client:

1. Trigger your client's MCP auth command (Claude Code uses `/mcp`; Cursor uses *Reload MCP
   servers*; check your client's docs).
2. Browser opens → sign in to your OKX **Affiliate** account.
3. On the consent screen, **toggle Live Trading ON**, leave Read-only on, and leave Trade /
   Earn / Demo trading **off**. Click *Authorize access*.
4. Your client should report success.

See [`claude-code.md#authentication`](claude-code.md#authentication) for screenshots of each
step — the OKX side is identical no matter which client triggered the flow.

## What to do if your client does not support custom OAuth resource params

Some clients ship MCP support that does not implement the
[RFC 8707 *resource indicator*](https://datatracker.ietf.org/doc/html/rfc8707) flow that OKX
requires. Symptom: OAuth completes but every tool call returns `invalid_grant: resource does
not match` or a 401 with `WWW-Authenticate: Bearer resource_metadata=...`.

In that case, follow the OpenClaw path — see [`openclaw.md`](openclaw.md). The skill there is
not OpenClaw-specific; the Python scripts can be adapted to any environment that lets you
inject a bearer token into outgoing MCP requests.

## Smoke-test

Ask your agent:

> *Show me my affiliate performance.*

A non-empty response with `depAmt`, `inviteeCnt`, and a `details[]` array (Spot / Derivative
/ BSC breakdown) means you are good. If it is empty, double-check that the OKX account you
authorized is the one enrolled as an Affiliate.

## Troubleshooting

See the [project FAQ](../faq.md) for common errors and fixes.
