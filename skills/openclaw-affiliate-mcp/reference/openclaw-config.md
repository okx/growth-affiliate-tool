# Wiring the token into OpenClaw

This skill stops at producing a valid `~/.openclaw/data/okx-affiliate-mcp/token.json`. How you make OpenClaw use that token to call the MCP is intentionally **out of scope** — it depends on the OpenClaw version and the MCP transport configuration in use.

This file is a placeholder for project-specific wiring notes. Update it as integration patterns stabilize.

## Likely shapes

- **HTTP MCP entry with bearer header**: configure OpenClaw to call `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp` with `Authorization: Bearer <token>`, where the token is read from `token.json`.
- **Dedicated bridge tool**: a small wrapper that reads `token.json`, optionally calls `refresh.py` if the token is near expiry, and forwards MCP calls.
- **Cron-driven refresh**: schedule `refresh.py` every ~50 minutes so consumers always see a fresh token.

Pick whichever your OpenClaw build supports. The skill itself is transport-agnostic.
