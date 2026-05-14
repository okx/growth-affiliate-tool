# Known issues / gotchas

These are real failures we hit during the original integration. Read this first when debugging.

## `invalid_grant: resource does not match`

**Cause:** the `resource` parameter is missing or different between the authorize request and the token request.

**Fix:** include `resource=https://www.okx.com/api/v1/mcp/growth-affiliate-mcp` on:
- the authorize URL (Step 2)
- the `authorization_code` token exchange (Step 3)
- the `refresh_token` token exchange (Step 4)

The skill's scripts all do this; if you bypass them, mirror the same value.

## Authorize page renders something other than OAuth approval

**Cause:** missing `flow=code` query parameter on the authorize URL.

**Fix:** keep `flow=code` in the authorize URL.

## `localhost:8787/callback` shows "site can't be reached" / blank page

**Expected and required.** There is no local server. The OAuth `code` is in the URL bar of the failed redirect; the user just needs to copy the address bar and paste it back.

This is the #1 user confusion during install. See `reference/blank-callback-page.md` for the full talk-through and the wording the agent should use with the user.

## Refresh returns 4xx

OKX revokes refresh tokens on certain account events (password change, app revoked, etc). When `refresh.py` exits with code 2:
- `client.json` is still valid; do **not** re-run `register.py`
- Re-run `auth.py` → user re-authorizes → `exchange.py`

## Multiple installs / multiple Affiliate accounts

Each install needs its own `client.json` (its own DCR registration). If a user wants to switch OKX accounts, the cleanest reset is:

```bash
rm -rf ~/.openclaw/data/okx-affiliate-mcp
```

Then run the full flow again.

## Why we don't use OpenClaw mcporter

OpenClaw's mcporter has an OAuth handler, but as of testing it does not handle:
- the mandatory `resource` parameter on OKX's authorize/token calls
- DCR against OKX's non-standard registration endpoint

So we manage the OAuth dance manually with this skill, and the resulting `access_token` is consumed by whatever transport OpenClaw is configured to use for the HTTP MCP call.
