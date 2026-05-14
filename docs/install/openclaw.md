# Install on OpenClaw

[← Back to install index](../../README.md#quick-start)

OpenClaw needs a slightly different install path because its built-in MCP runtime does **not**
yet handle two of OKX's OAuth quirks:

1. The **mandatory `resource` parameter** ([RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707))
   on every authorize and token request.
2. The **non-discovery DCR (Dynamic Client Registration) endpoint** at
   `/api/v5/mcp/auth/register`.

Most other MCP clients (Claude Code, Codex) handle these natively. Until
OpenClaw upstream catches up, OpenClaw users install via the **bundled skill** in this repo
at [`skills/openclaw-affiliate-mcp/`](../../skills/openclaw-affiliate-mcp/) — a few small
Python scripts plus an agent-readable decision tree.

## What the skill provides

- [`SKILL.md`](../../skills/openclaw-affiliate-mcp/SKILL.md) — agent-readable decision tree
- [`scripts/register.py`](../../skills/openclaw-affiliate-mcp/scripts/register.py) — DCR (one-time per install)
- [`scripts/auth.py`](../../skills/openclaw-affiliate-mcp/scripts/auth.py) — build authorize URL + PKCE
- [`scripts/exchange.py`](../../skills/openclaw-affiliate-mcp/scripts/exchange.py) — exchange code for tokens
- [`scripts/refresh.py`](../../skills/openclaw-affiliate-mcp/scripts/refresh.py) — refresh access token (run before 1 h expiry)
- [`reference/`](../../skills/openclaw-affiliate-mcp/reference/) — endpoint specs, known issues, callback page tips

All scripts are stdlib-only — no `pip install` required.

## Install

### Option A — full repo clone (simplest)

```bash
git clone https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cp -r /tmp/growth-affiliate-tool/skills/openclaw-affiliate-mcp \
      ~/.openclaw/workspace/skills/okx-affiliate-mcp
```

### Option B — sparse checkout (only the skill)

```bash
git clone --filter=blob:none --sparse \
  https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cd /tmp/growth-affiliate-tool && git sparse-checkout set skills/openclaw-affiliate-mcp
cp -r skills/openclaw-affiliate-mcp ~/.openclaw/workspace/skills/okx-affiliate-mcp
```

Either way, ask your OpenClaw agent:

> *Install the OKX Affiliate MCP.*

The agent loads `SKILL.md`, runs the four scripts in order, and walks you through the OAuth
flow. The whole thing takes ~2 minutes.

## What to expect during OAuth

The skill produces a regular OKX OAuth URL. After you click *Authorize* on OKX:

- ⚠️ Your browser will land on a **blank / "site can't be reached" page** at
  `localhost:8787/callback?...`. **This is expected.** OKX has finished its work — there is
  no local server running on your machine, but we just need the URL.
- **Copy the entire URL from your browser's address bar** and paste it back into chat.
- The agent extracts the `code` parameter, calls `exchange.py`, and you are connected.

Full instructions for handling the callback page (and what to tell users who panic about the
blank page) live in
[`skills/openclaw-affiliate-mcp/SKILL.md`](../../skills/openclaw-affiliate-mcp/SKILL.md) and
[`skills/openclaw-affiliate-mcp/reference/blank-callback-page.md`](../../skills/openclaw-affiliate-mcp/reference/blank-callback-page.md).

## Token lifecycle

`token.json` lives at `~/.openclaw/data/okx-affiliate-mcp/token.json`. It contains:

- `access_token` — used for every MCP call (1-hour lifetime)
- `refresh_token` — used to mint new access tokens
- `obtained_at` — Unix seconds, written by the skill

Run `scripts/refresh.py` whenever the access token gets close to expiring; the skill's
decision tree handles this automatically.

## Wiring into OpenClaw's MCP config

Once `token.json` is populated, point OpenClaw at the MCP endpoint with the bearer token from
the file. See
[`skills/openclaw-affiliate-mcp/reference/openclaw-config.md`](../../skills/openclaw-affiliate-mcp/reference/openclaw-config.md)
for the current recommended wiring.

## When OpenClaw upstream supports custom OAuth

The skill becomes unnecessary the day OpenClaw's mcporter handles the `resource` parameter
and the custom DCR endpoint. At that point the install path collapses to the standard JSON
config used by every other native-OAuth client. We will update this guide when that happens.

## Troubleshooting

| Symptom                                              | Fix                                                      |
| ---------------------------------------------------- | -------------------------------------------------------- |
| `invalid_grant: resource does not match`             | The skill missed adding the `resource` param — re-run `auth.py` and `exchange.py` from a clean state |
| Browser shows blank page after Authorize             | **Expected.** Copy the URL from the address bar         |
| `refresh.py` returns 4xx                             | Refresh token is dead. Re-run `auth.py` + `exchange.py` (skip `register.py`, `client.json` is still valid) |
| MCP calls return 401 even right after token refresh  | Restart your OpenClaw session so it picks up new headers |

For deeper debugging see
[`skills/openclaw-affiliate-mcp/reference/known-issues.md`](../../skills/openclaw-affiliate-mcp/reference/known-issues.md).
