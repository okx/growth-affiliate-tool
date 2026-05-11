# Agent install bootstrap

> This file is written for **AI agents**. It is a decision tree that lets an agent install the
> OKX Growth Affiliate Tool MCP without first parsing the human-facing README.
>
> If you are a human, you probably want [`README.md`](README.md) instead.

## Endpoint (memorize)

```
URL:        https://www.okx.com/api/v1/mcp/growth-affiliate-mcp
Transport:  http (Streamable HTTP)
Auth:       OAuth 2.0, hosted by OKX
```

## Decision tree

```
Q1: What runtime are you running inside?

├── Claude Code (the `claude` CLI)
│       → docs/install/claude-code.md
│
├── Codex CLI
│       → docs/install/codex.md
│
├── Hermes
│       → docs/install/hermes.md
│
├── Cursor
│       → docs/install/cursor.md
│
├── OpenClaw  ← OAuth NOT handled natively
│       → docs/install/openclaw.md
│         (uses bundled skill at: skills/openclaw-affiliate-mcp/)
│
└── Other MCP-compliant client with native OAuth
        → docs/install/generic.md
```

## Universal four-step flow (for native-OAuth clients)

After registering the MCP via the client-specific command/file:

1. **Trigger OAuth** — run the client's MCP auth command (`/mcp` in Claude Code, etc.).
2. **Tell the user** — a browser window will open. They must:
   - Sign in to the OKX Affiliate account they want connected.
   - On the consent screen, **leave Live Trading → Read-only checked**, leave everything
     else **off**, then click *Authorize access*.
3. **Wait** — the agent's terminal will show *Authentication successful*.
4. **Verify** — call `okx-affiliate-performance-summary` with no arguments. A 200 with
   `data[0].details[].commission` and `vol` numbers means you are good.

> ⚠️ Do **not** request `live:trade`, `live:earn`, or `live:asset_transfer` — this MCP only
> needs read scope. Asking for write scopes is unnecessary and will alarm the user.

## Scope mapping (what to tell the user to check)

| OKX consent toggle  | Tell the user                     |
| ------------------- | --------------------------------- |
| Live trading        | **ON** (this is the read scope)   |
| Read-only           | **ON** (default — leave it on)    |
| Trade               | OFF                               |
| Earn                | OFF                               |
| Demo trading        | OFF                               |

## Common error responses (full list in `docs/faq.md`)

| Symptom                                                | Likely cause                                | Action                                      |
| ------------------------------------------------------ | ------------------------------------------- | ------------------------------------------- |
| `401 Unauthorized` after install                        | OAuth not yet completed                     | Run the client's MCP auth command           |
| `401` after working previously                          | Access token expired (lifetime ≈ 1 h)        | Most clients refresh automatically — re-run the request, or trigger MCP reconnect |
| `500 system error` from `okx-affiliate-invitee-list`    | `limit` was ≥ 99 (server bug)               | Use `"limit": "95"` or smaller |
| `okx-affiliate-link-list` filter ignored               | Invalid enum (typo, wrong case)             | Use lowercase exact values: `standard`/`co_inviter`, `normal`/`abnormal` |
| `invalid_grant: resource does not match`               | Custom OAuth client missing `resource` param | Use a supported client (see Q1) — only OpenClaw is known to need the skill workaround |

## After install succeeds

Point the agent at:

- [`docs/tools-reference.md`](docs/tools-reference.md) — every tool's parameters
- [`docs/period-type.md`](docs/period-type.md) — the eight time-window codes
- [`docs/usage-examples.md`](docs/usage-examples.md) — natural-language prompt patterns
